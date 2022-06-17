"""This is the C2 Server Class which handles the devices & listeners"""


class ServerClass():
    """This is the C2 Server Class which handles the devices & listeners"""

    def __init__(self):
        self.active_devices_count = 0
        self.active_listeners_count = 0
        self.active_listeners = {}
        self.active_devices = {}

    def get_device(self, device_id):
        """Get a device by id"""
        try:
            return self.active_devices[str(device_id)]
        except ValueError:
            raise Exception("Invalid ID") from None
        except IndexError:
            raise Exception("Device does not exist") from None

    def get_listener(self, listener_id):
        """Get a listener by id"""
        try:
            return self.active_listeners[str(listener_id)]
        except ValueError:
            raise Exception("Invalid ID") from None
        except IndexError:
            raise Exception("Listener does not exist") from None

    def add_listener(self, listener):
        """Add a listener to the server"""
        self.active_listeners_count += 1
        self.active_listeners[str(listener.id)] = listener

    def add_device(self, device):
        """Add a device to the server"""
        self.active_devices_count += 1
        self.active_devices[str(device.id)] = device

    def remove_listener(self, listener_id):
        """Remove a listener from the server"""
        try:
            self.active_listeners.pop(str(listener_id))
            self.active_listeners_count -= 1
        except ValueError:
            raise Exception("Invalid ID") from None
        except IndexError:
            raise Exception("Listener does not exist") from None

    def remove_device(self, device_id):
        """Remove a device from the server"""
        try:
            self.active_devices.pop(device_id + 1)
            self.active_devices_count -= 1
        except ValueError:
            raise Exception("Invalid ID") from None
        except IndexError:
            raise Exception("Device does not exist") from None
