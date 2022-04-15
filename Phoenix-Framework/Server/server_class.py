class Server_Class():
    """This is the C2 Server Class which handles the devices & listeners"""
    def __init__(self):
        self.listeners = []
        self.devices = []
    def get_device(self, id):
        # Get a device by id
        try:
            id = int(id) - 1
            return self.devices[id]
        except ValueError:
            return Exception("Invalid ID")
        except IndexError:
            raise Exception("Device does not exist")
    def get_listener(self, id):
        # Get a listener by id
        try:
            id = int(id) - 1
            return self.listeners[id]
        except ValueError:
            return Exception("Invalid ID")
        except IndexError:
            raise Exception("Listener does not exist")
    def add_listener(self, listener):
        # Add a listener to the server
        self.listeners.append(listener)
    def add_device(self, device):
        # Add a device to the server
        self.devices.append(device)
    def remove_listener(self, id):
        # Remove a listener from the server
        try:
            id = int(id) - 1
            self.listeners.pop(id)
        except ValueError:
            return Exception("Invalid ID")
        except IndexError:
            raise Exception("Listener does not exist")
    def remove_device(self, id):
        # Remove a device from the server
        try:
            id = int(id) - 1
            self.devices.pop(id)
        except ValueError:
            return Exception("Invalid ID")
        except IndexError:
            raise Exception("Device does not exist")