
from Utils import *
from Server import Server_Class
class Base_Listener():
    """This is the Parent Class for all Listeners"""
    def __init__(self, server, config, id):
        self.address = config["address"]
        self.server : Server_Class = server
        self.port = config["port"]
        self.id = id
        self.devices = []

    def decrypt(self, data) -> str:
        """Decrypt received Data"""
        return self.fernet.decrypt(data).decode()

    def encrypt(self, data) -> bytes:
        """Encrypt Data"""
        return self.fernet.encrypt(data.encode())
    def add_device(self, device):
        """Add a Device to the Listener"""
        self.devices.append(device)
    def remove_device(self, device):
        """Remove a Device from the Listener"""
        self.devices.remove(device)