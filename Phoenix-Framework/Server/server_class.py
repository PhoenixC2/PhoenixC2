from Handlers.base import Base_Handler
"""This is the C2 Server Class which handles the devices & listeners"""


class ServerClass():
    """This is the C2 Server Class which handles the devices & listeners"""

    def __init__(self):
        self.active_handlers_count = 0
        self.active_listeners_count = 0
        self.active_listeners = {}
        self.active_handlers = {}

    def get_handler(self, handler_id):
        """Get a handler by id"""
        try:
            return self.active_handlers[str(handler_id)]
        except ValueError:
            raise Exception("Invalid ID") from None
        except IndexError:
            raise Exception("Handler does not exist") from None

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

    def add_handler(self, handler: Base_Handler):
        """Add a handler to the server"""
        self.active_handlers_count += 1
        self.active_handlers[str(handler.id)] = handler

    def remove_listener(self, listener_id: int):
        """Remove a listener from the server"""
        try:
            self.active_listeners.pop(str(listener_id))
            self.active_listeners_count -= 1
        except ValueError:
            raise Exception("Invalid ID") from None
        except IndexError:
            raise Exception("Listener does not exist") from None

    def remove_handler(self, handler_id: int):
        """Remove a device from the server by id"""
        try:
            self.active_handlers.pop(str(handler_id))
            self.active_handlers_count -= 1
        except ValueError:
            raise Exception("Invalid ID") from None
        except IndexError:
            raise Exception("Handler does not exist") from None
