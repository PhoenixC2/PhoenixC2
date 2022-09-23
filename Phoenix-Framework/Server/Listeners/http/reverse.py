import uuid
from typing import TYPE_CHECKING
from datetime import datetime
from multiprocessing import Process
from threading import Thread

from Database import DeviceModel, db_session, ListenerModel
from flask import Flask, request, Response
from Creator.available import AVAILABLE_ENCODINGS, AVAILABLE_FORMATS
from Handlers.http.reverse import Handler
from Listeners.base import BaseListener
from Utils.options import (AddressType, BooleanType, IntegerType, Option, TableType, ChoiceType,
                           OptionPool, StringType)
from Utils.ui import ph_print

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
            type=TableType(lambda : db_session.query(ListenerModel).all(), ListenerModel),
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
        self.listener_process: Process
        self.create_api()

    def create_api(self):
        self.api = Flask(__name__)

        @self.api.route("/connect", methods=["POST"])
        def connect():
            data = request.get_json()
            try:
                device = DeviceModel(
                    name=str(uuid.uuid1()),
                    hostname=data.get("hostname", ""),
                    address=data.get("address"),
                    connection_date=datetime.now(),
                    last_online=datetime.now(),
                    listener=self.db_entry
                )
            except: 
                return 400
            db_session.add(device)
            db_session.commit()
            ph_print(f"New Device ({device.hostname}) connected to the server. [{device.name}]")
            return device.name

        @self.api.after_request
        def change_headers(r: Response):
            return r

    def start(self):
        if self.ssl:
            self.listener_process = Process(target=self.api.run,
                                            kwargs={
                                                "host": self.address,
                                                "port": self.port,
                                                "ssl_context": ("Data/ssl.pem", "Data/ssl.key"),
                                                "threaded": True},
                                            name=self.db_entry.name)
        else:
            self.listener_process = Process(target=self.api.run,
                                            kwargs={
                                                "host": self.address,
                                                "port": self.port,
                                                "threaded": True},
                                            name=self.db_entry.name)
        Thread(target=self.listener_process.start).start()

    def stop(self):
        self.listener_process.kill()

    def status(self) -> True:
        return self.listener_process.is_alive()
