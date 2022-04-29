class Server_Class():
    """This is the C2 Server Class which handles the devices & listeners"""
    
    def __init__(self):
        self.active_devices_count = 0
        self.active_listeners_count = 0
        self.active_listeners = {}
        self.active_devices = {}
    def get_device(self, id):
        """Get a device by id"""
        try:
            id = int(id) - 1
            return self.active_devices[id]
        except ValueError:
            return Exception("Invalid ID")
        except IndexError:
            raise Exception("Device does not exist")
    def get_listener(self, id):
        """Get a listener by id"""
        try:
            id = int(id) - 1
            return self.active_listeners[str(id)]
        except ValueError:
            return Exception("Invalid ID")
        except IndexError:
            raise Exception("Listener does not exist")
    def add_listener(self, listener):
        """Add a listener to the server"""
        self.active_listeners[str(listener.id)] = listener
    def add_device(self, device):
        """Add a device to the server"""
        self.active_devices[str(device.id)] = device
    def remove_listener(self, id):
        """Remove a listener from the server"""
        try:
            self.active_listeners.pop(str(id))
        except ValueError:
            return Exception("Invalid ID")
        except IndexError:
            raise Exception("Listener does not exist")
    def remove_device(self, id):
        """Remove a device from the server"""
        try:
            self.active_devices.pop(str(id))
        except ValueError:
            return Exception("Invalid ID")
        except IndexError:
            raise Exception("Device does not exist")