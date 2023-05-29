import logging
import os
from datetime import datetime
from threading import Thread
from typing import TYPE_CHECKING

from flask import Flask, Response, cli, jsonify, request, send_from_directory

from phoenixc2.server.database import (
    DeviceModel,
    ListenerModel,
    LogEntryModel,
    Session,
    StagerModel,
    TaskModel,
)
from phoenixc2.server.utils.features import Feature
from phoenixc2.server.utils.options import DefaultListenerPool, Option, StringType
from phoenixc2.server.utils.resources import get_resource
from phoenixc2.server.utils.web import FlaskThread

from ..listener_base import BaseListener
from .handler import Handler

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander


class Listener(BaseListener):
    """The Reverse Http Listener Class"""

    name = "http-reverse"
    description = (
        "Listener based on the http protocol "
        "that uses a stager to connect back to the server"
    )
    author: str = "Screamz2k"
    protocol: str = "http"
    os = ["linux", "windows", "osx"]
    option_pool = DefaultListenerPool(
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
                    f"A Stager is trying to connect to '{self.db_entry.name}'"
                    "but the listeners limit is reached.",
                )
                return "", 404
            try:
                hostname = data.get("hostname", "")
                os = data.get("os", "")
                architecture = data.get("architecture", "")
                user = data.get("user", "")
                admin = data.get("admin", False)
                stager_id = data.get("stager", "")
                uid = data.get("uid", "")

                stager = Session.query(StagerModel).filter_by(id=stager_id).first()

                if stager is None:
                    LogEntryModel.log(
                        "error",
                        "listeners",
                        f"A Stager is trying to connect to '{self.db_entry.name}'"
                        "but the stager id is invalid.",
                    )
                    raise ValueError("Invalid Stager ID")
                device, reconnect = DeviceModel.register(
                    hostname,
                    request.remote_addr,
                    os,
                    architecture,
                    user,
                    admin,
                    stager,
                    uid,
                )
            except Exception:
                return "", 404

            if not reconnect:
                Session.add(device)

            Session.commit()
            self.commander.new_connection(device, reconnect=reconnect)
            self.add_handler(Handler(device, self))
            return jsonify({"name": device.name})

        @self.api.route("/tasks/<string:device_name>")
        def get_tasks(device_name: str = None):
            if device_name is None:
                return "", 400
            handler = self.get_handler(device_name)
            if handler is None:
                device: DeviceModel = (
                    Session.query(DeviceModel).filter_by(name=device_name).first()
                )
                if device is not None:
                    handler = Handler(device, self)
                    self.add_handler(handler)
                    self.commander.new_connection(device, reconnect=True)
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

        @self.api.route("/finish/<string:task_name>", methods=["POST"])
        def finish_task(task_name: str = None):
            if task_name is None:
                return "", 404

            task: TaskModel = Session.query(TaskModel).filter_by(name=task_name).first()

            if task is None:
                return "", 404

            data = request.get_json()
            output = data.get("output", "")
            success = data.get("success", "")
            credentials = data.get("creds", [])

            task.finish(output, success, credentials)
            Session.commit()
            return "", 200

        @self.api.route("/update/<string:device_name>", methods=["POST"])
        def update_task_output(device_name: str = None):
            """Update the output of a task in the database"""
            if device_name is None:
                return "", 404

            handler = self.get_handler(device_name)
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
            LogEntryModel.log(
                "info",
                "listeners",
                f"Updated output of task {task_id} for device {device_name}",
            )
            return "", 200

        @self.api.route("/download/<string:task_name>", methods=["GET"])
        def download(task_name: str = None):
            if task_name is None:
                return "", 404

            return send_from_directory(
                str(get_resource("data/uploads")),
                task_name,
                as_attachment=True,
            )

        @self.api.route("/module/<string:task_name>", methods=["GET"])
        def get_module_info(task_name: str = None):
            task: TaskModel = Session.query(TaskModel).filter_by(name=task_name).first()

            if task is None:
                return "", 404
            try:
                module = task.get_module()
            except Exception:
                return "", 404

            return jsonify(module.to_dict(self.commander))

        @self.api.route("/module/download/<string:task_name>", methods=["GET"])
        def download_module_content(task_name: str = None):
            task: TaskModel = Session.query(TaskModel).filter_by(name=task_name).first()

            if task is None:
                return "", 404
            try:
                module = task.get_module()
            except Exception:
                return "", 404

            return module.code(task)

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
