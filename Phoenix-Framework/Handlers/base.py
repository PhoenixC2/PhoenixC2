from Utils import *

class Base_Handler():
    """The Base Handler Class for all Devices"""

    def __str__(self) -> str:
        return str(self.addr[0])

    def __init__(self, conn, addr, key, id):
        self.conn = conn
        self.addr = addr
        self.key = key
        self.fernet = Fernet(key)
        self.id = id

    def decrypt(self, data):
        """Decrypt the data"""
        return self.fernet.decrypt(data).decode()

    def encrypt(self, data):
        """Encrypt the data"""
        return self.fernet.encrypt(data.encode())