from Utils import *

class Base_Handler():
    """The Base Handler Class for all Devices"""

    def __str__(self) -> str:
        return str(self.addr)

    def __init__(self, addr, key, id):
        self.addr = addr
        self.key = key
        self.fernet = Fernet(key)
        self.id = id
        self.modules = []

    def decrypt(self, data):
        """Decrypt the data"""
        return self.fernet.decrypt(data).decode()

    def encrypt(self, data):
        """Encrypt the data"""
        return self.fernet.encrypt(data.encode())
    def load_module(self, name):
        """Load a module"""
        # Get module
        module = importlib.import_module("Modules." + name).Module()
        # Add to list
        self.modules.append(module)
        # Return module
        return module
    def unload_module(self, name):
        """Unload a module"""
        # Get module
        for module in self.modules:
            if module.name == name:
                self.modules.remove(module)
                return module
        raise Exception("Module not found")
