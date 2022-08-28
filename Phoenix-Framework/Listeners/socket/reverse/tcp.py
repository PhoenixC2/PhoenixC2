"""Reverse Socket TCP Listener"""
from Utils.libraries import socket, ssl, log, time, Fernet, threading
from Handlers.socket.reverse.tcp.linux import Linux
from Handlers.socket.reverse.tcp.windows import Windows
from Listeners.base import BaseListener


class Listener(BaseListener):
    """The Reverse Tcp Listener Class"""

    def __init__(self, server, config, listener_id):
        super().__init__(server, config, listener_id)
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
            target=self.refresh_connections, name="Refresher")

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
            except socket.timeout:
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
                except socket.error:
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
                            self.server.active_handlers_count + 1))
                elif operating_system == "linux":
                    # Create a Linux Object to store the connection
                    self.add_handler(
                        Linux(
                            connection, addr[0],
                            key,
                            self.server.active_handlers_count + 1))
                else:
                    log(f"Unknown Operating System: {operating_system}",
                        alert="error")
                    connection.close()
                    continue

    def start(self):
        try:
            self.listener.bind((self.address, self.port))
            self.listener.listen()
        except socket.error:
            raise Exception("Port is already in use.") from None
        # Start the Listener and Refresher
        self.listener_thread.start()
        self.refresher_thread.start()

    def stop(self):
        self.stopped = True