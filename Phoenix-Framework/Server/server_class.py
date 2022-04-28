class Server_Class():
    """This is the C2 Server Class which handles the devices & listeners"""
    
    def __init__(self):
        self.all_devices = 0
        self.all_listeners = 0
        self.listeners = {}
        self.devices = {}
    def get_device(self, id):
        """Get a device by id"""
        try:
            id = int(id) - 1
            return self.devices[id]
        except ValueError:
            return Exception("Invalid ID")
        except IndexError:
            raise Exception("Device does not exist")
    def get_listener(self, id):
        """Get a listener by id"""
        try:
            id = int(id) - 1
            return self.listeners[str(id)]
        except ValueError:
            return Exception("Invalid ID")
        except IndexError:
            raise Exception("Listener does not exist")
    def add_listener(self, listener):
        """Add a listener to the server"""
        self.listeners[str(listener.id)] = listener
    def add_device(self, device):
        """Add a device to the server"""
        self.devices[str(device.id)] = device
    def remove_listener(self, id):
        """Remove a listener from the server"""
        try:
            self.listeners.pop(str(id))
        except ValueError:
            return Exception("Invalid ID")
        except IndexError:
            raise Exception("Listener does not exist")
    def remove_device(self, id):
        """Remove a device from the server"""
        try:
            self.devices.pop(str(id))
        except ValueError:
            return Exception("Invalid ID")
        except IndexError:
            raise Exception("Device does not exist")