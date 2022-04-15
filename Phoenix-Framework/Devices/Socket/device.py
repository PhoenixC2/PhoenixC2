from Utils import *

class Base_Device():
    """The Linux Device Class to interact with the Device"""

    def __str__(self) -> str:
        return str(self.addr[0])

    def __init__(self, conn, addr, key):
        self.conn = conn
        self.addr = addr
        self.key = key
        self.fernet = Fernet(key)

    def decrypt(self, data):
        # Decrypt the data
        return self.fernet.decrypt(data).decode()

    def encrypt(self, data):
        # Encrypt the data
        return self.fernet.encrypt(data.encode())