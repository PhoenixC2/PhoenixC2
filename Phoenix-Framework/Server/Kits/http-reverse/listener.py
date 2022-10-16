import logging
import os
import time
from datetime import datetime
from threading import Thread
from typing import TYPE_CHECKING

from Database import DeviceModel, ListenerModel, Session
from flask import Flask, Response, cli, jsonify, request
from Utils.options import DefaultListenerPool, Option, StringType
from Utils.ui import log, log_connection
from Utils.web import FlaskThread

from ..base_listener import BaseListener
from .handler import Handler

if TYPE_CHECKING:
    from Commander import Commander


class Listener(BaseListener):
    """The Reverse Http Listener Class"""
    name = "http-reverse"
    description = "Reverse HTTP Listener"
    os = ["linux", "windows", "osx"]
    api = Flask(__name__)
    options = DefaultListenerPool([
        Option(
            name="Server Header",
            _real_name="header",
            description="The Server Header to return",
            type=StringType,
            default="Werkzeug/2.2.2 Python/3.10.7"
        )
    ])

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
            data = request.get_json()
            if len(self.handlers) >= self.db_entry.limit:
                log(
                    f"A Stager is trying to connect to '{self.db_entry.name}' but the listeners limit is reached.", "info")
                return "", 404
            try:
                address = data.get("address")
                hostname = data.get("hostname", "")
                os = data.get("os", "")
                device = DeviceModel.generate_device(
                    self, hostname, address, os)
            except Exception:
                return "", 404
            Session.add(device)
            Session.commit()
            log_connection(device)
            self.add_handler(Handler(device))
            return device.name

        @self.api.route("/tasks/<string:name>")
        def get_tasks(name: str = None):
            if name is None:
                return "", 400
            handler = self.get_handler(name)
            if handler is None:
                device: DeviceModel = Session.query(
                    DeviceModel).filter_by(name=name).first()
                if device is not None:
                    handler = Handler(device)
                    self.add_handler(handler)
                    log_connection(device, reconnect=True)
                else:
                    return "", 404
            handler.db_entry.last_online = datetime.now()  # update last online
            Session.commit()
            return jsonify([task.to_dict(self.commander, False) for task in handler.db_entry.tasks if task.finished_at is None])

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
            Session.commit()
            return "", 200

        @self.api.after_request
        def change_headers(r: Response):
            return r

    def start(self):
        if not "2" in os.getenv("PHOENIX_DEBUG", "") and not "4" in os.getenv("PHOENIX_DEBUG", ""):
            cli.show_server_banner = lambda *args: None
            logging.getLogger("werkzeug").disabled = True
        self.listener_thread = FlaskThread(
            self.api, self.address, self.port, self.ssl, self.db_entry.name)
        self.refresher_thread = Thread(target=self.refresh_connections,
                                       name=self.db_entry.name+"-Refresher-Thread")
        self.listener_thread.start()
        self.refresher_thread.start()

    def stop(self):
        self.stopped = True
        self.listener_thread.shutdown()

    def status(self) -> True:
        return self.process.is_alive()
