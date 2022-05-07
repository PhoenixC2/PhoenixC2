from Utils import *
from Server import Server_Class
class Base_Listener():
    """This is the Base Class for all Listeners"""
    def __init__(self, server, config, id):
        self.address = config["address"]
        self.port = config["port"]
        self.ssl = True if config["ssl"].lower() == "true" else False
        self.server : Server_Class = server
        self.id = id
        self.devices = {}

    def decrypt(self, data) -> str:
        """Decrypt Data"""
        return self.fernet.decrypt(data).decode()

    def encrypt(self, data) -> bytes:
        """Encrypt Data"""
        return self.fernet.encrypt(data.encode())
    
    def add_device(self, device):
        """Add a Device to the Listener"""
        self.devices[str(device.id)] = device
        self.server.add_device(device)
    
    def remove_device(self, device):
        """Remove a Device from the Listener"""
        self.devices.pop(str(device.id))
        self.server.remove_device(device)
