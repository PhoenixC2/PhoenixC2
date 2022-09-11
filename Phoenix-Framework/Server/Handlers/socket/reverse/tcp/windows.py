from Handlers.base import BaseHandler


class Windows(BaseHandler):
    """The Windows Device Class to interact with the Device"""

    def __init__(self, connection, address, key, id):
        super().__init__(address, key, id)
        self.conn = connection

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
