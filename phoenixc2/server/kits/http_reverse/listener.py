import logging
import os
from datetime import datetime
from threading import Thread
from typing import TYPE_CHECKING

from flask import Flask, Response, cli, jsonify, request, send_from_directory

from phoenixc2.server.database import (DeviceModel, ListenerModel, LogEntryModel,
                                     Session, StagerModel, TaskModel)
from phoenixc2.server.modules import get_module
from phoenixc2.server.utils.features import Feature
from phoenixc2.server.utils.options import (DefaultListenerPool, Option,
                                          StringType)
from phoenixc2.server.utils.resources import get_resource
from phoenixc2.server.utils.ui import log_connection
from phoenixc2.server.utils.web import FlaskThread

from ..base_listener import BaseListener
from .handler import Handler

if TYPE_CHECKING:
    from phoenixc2.server.commander import Commander


class Listener(BaseListener):
    """The Reverse Http Listener Class"""

    name = "http-reverse"
    description = "Reverse HTTP Listener"
    author: str = "Screamz2k"
    os = ["linux", "windows", "osx"]
    options = DefaultListenerPool(
        [
            Option(
                name="Server Header",
                real_name="header",
                description="The Server Header to return",
                type=StringType(),
                default="Werkzeug/2.2.2 Python/3.10.7",
            )
        ]
    )
    features = [
        Feature(
            name="https",
            description="Encrypted traffic using https",
        ),
        Feature(
            name="Normal Traffic",
            description="Http is a widely used protocol",
        ),
    ]

    def __init__(self, commander: "Commander", db_entry: ListenerModel):
        super().__init__(commander, db_entry)
        self.stopped = False
        self.listener_thread: FlaskThread
        self.refresher_thread: Thread
        self.create_api()

    def create_api(self):
        self.api = Flask(__name__)

        @self.api.route("/connect", methods=["POST"])
        def connect():
            data: dict = request.get_json()
            if len(self.handlers) >= self.db_entry.limit:
                LogEntryModel.log(
                    "error",
                    "listeners",
                    f"A Stager is trying to connect to '{self.db_entry.name}' but the listeners limit is reached.",
                )
                return "", 404
            try:
                address = data.get("address")
                hostname = data.get("hostname", "")
                os = data.get("os", "")
                architecture = data.get("architecture", "")
                user = data.get("user", "")
                admin = data.get("admin", False)
                stager_id = data.get("stager", "")

                stager = Session.query(StagerModel).filter_by(id=stager_id).first()

                if stager is None:
                    LogEntryModel.log(
                        "error",
                        "listeners",
                        f"A Stager is trying to connect to '{self.db_entry.name}' but the stager id is invalid.",
                    )
                    raise ValueError("Invalid Stager ID")
                device = DeviceModel.generate_device(
                    hostname, address, os, architecture, user, admin, stager
                )
            except Exception as e:
                return "", 404
            Session.add(device)
            Session.commit()
            log_connection(device)
            self.add_handler(Handler(device, self))
            return device.name

        @self.api.route("/tasks/<string:name>")
        def get_tasks(name: str = None):
            if name is None:
                return "", 400
            handler = self.get_handler(name)
            if handler is None:
                device: DeviceModel = (
                    Session.query(DeviceModel).filter_by(name=name).first()
                )
                if device is not None:
                    handler = Handler(device, self)
                    self.add_handler(handler)
                    log_connection(device, reconnect=True)
                else:
                    return "", 404
            handler.db_entry.last_online = datetime.now()  # update last online
            Session.commit()
            return jsonify(
                [
                    task.to_dict(self.commander, False)
                    for task in handler.db_entry.tasks
                    if task.finished_at is None
                ]
            )

        @self.api.route("/finish/<string:name>", methods=["POST"])
        def finish_task(name: str = None):
            if name is None:
                return "", 404

            handler = self.get_handler(name)
            if handler is None:
                return "", 404

            data = request.get_json()
            task_id = data.get("id", "")
            output = data.get("output", "")
            success = data.get("success", "")

            task = handler.get_task(task_id)
            if task is None:
                return "", 404

            task.finish(output, success)
            return "", 200

        @self.api.route("/update/<string:name>", methods=["POST"])
        def update_task_output(name: str = None):
            """Update the output of a task in the database"""
            if name is None:
                return "", 404

            handler = self.get_handler(name)
            if handler is None:
                return "", 404

            data: dict = request.get_json()
            task_id = data.get("id", "")
            output = data.get("output", "")

            task = handler.get_task(task_id)
            if task is None:
                return "", 404

            task.output = output
            Session.commit()
            return "", 200

        @self.api.route("/download/<string:file_name>", methods=["GET"])
        def download(file_name: str = None):
            if file_name is None:
                return "", 404

            return send_from_directory(
                get_resource("downloads"),
                file_name,
                as_attachment=True,
            )

        @self.api.route("/module/<string:path>", methods=["GET"])
        def get_module_info(path: str = None):
            if path is None:
                return "", 404
            try:
                module = get_module(path)
            except Exception:
                return "", 404
            if module is None:
                return "", 404

            return jsonify(module.to_dict())

        @self.api.route("/module/download", methods=["GET"])
        def download_module_content(path: str = None):
            task_name = request.args.get("name", "")

            task: TaskModel = Session.query(TaskModel).filter_by(name=task_name).first()

            if task is None:
                return "", 404

            try:
                return task.get_module_code()
            except ValueError:
                return "", 404

        @self.api.after_request
        def change_headers(r: Response):
            r.headers["Server"] = self.db_entry.options["header"]
            return r

    def start(self):
        if "2" not in os.getenv("PHOENIX_DEBUG", "") and "4" not in os.getenv(
            "PHOENIX_DEBUG", ""
        ):
            cli.show_server_banner = lambda *args: None
            logging.getLogger("werkzeug").disabled = True
        self.listener_thread = FlaskThread(
            self.api, self.address, self.port, self.ssl, self.db_entry.name
        )
        self.refresher_thread = Thread(
            target=self.refresh_connections,
            name=self.db_entry.name + "-Refresher-Thread",
        )
        self.listener_thread.start()
        self.refresher_thread.start()

    def stop(self):
        self.stopped = True
        self.listener_thread.shutdown()

    def status(self) -> bool:
        return self.process.is_alive()
