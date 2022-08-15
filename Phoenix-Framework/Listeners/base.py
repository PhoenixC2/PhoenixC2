from Utils import Fernet
from Server import ServerClass
class Base_Listener():
    """This is the Base Class for all Listeners"""
    def __init__(self, server, config, id):
        self.address = config["address"]
        self.port = config["port"]
        self.ssl = True if str(config["ssl"]).lower() == "true" else False
        self.server : ServerClass = server
        self.id = id
        self.devices = {}

    def decrypt(self, data, key) -> str:
        """Decrypt Data"""
        return Fernet(key).decrypt(data).decode()

    def encrypt(self, data: str, key: str) -> bytes:
        """Encrypt Data"""
        return Fernet(key).encrypt(data.encode())
    
    def add_device(self, device):
        """Add a Device to the Listener"""
        self.devices[str(device.id)] = device
        self.server.add_handler(device)
    
    def remove_device(self, device):
        """Remove a Device from the Listener"""
        self.devices.pop(str(device.id))
        self.server.remove_handler(device)
