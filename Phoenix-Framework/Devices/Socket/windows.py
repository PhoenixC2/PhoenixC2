from Devices.Socket.device import Base_Device
class Windows(Base_Device):
    """The Windows Device Class to interact with the Device"""

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
