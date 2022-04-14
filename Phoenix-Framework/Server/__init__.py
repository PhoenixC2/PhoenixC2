from Server.args import *
from Server.services import *
from Utils import *
class Server():
    def __init__(self):
        self.listeners = []
        self.connections = []
    def get_device(self, id):
        # Get a connection by id
        try:
            id = int(id) - 1
            return self.connections[id]
        except ValueError:
            return Exception("Invalid ID")
        except IndexError:
            raise Exception("Connection does not exist")