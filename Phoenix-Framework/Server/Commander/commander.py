"""This is the C2 Server Class which handles the devices & listeners"""
from typing import Optional
from Handlers.base import BaseHandler
from Listeners.base import BaseListener


class Commander():
    """This is the Commander which handles the devices & listeners"""

    def __init__(self):
        self.active_handlers_count = 0
        self.active_listeners_count = 0
        self.active_listeners: dict[str, BaseListener] = {}
        self.active_handlers = {}

    def get_active_handler(self, handler_id: int) -> Optional[BaseHandler]:
        """Get a handler by id"""
        try:
            return self.active_handlers[str(handler_id)]
        except ValueError:
            raise Exception("Invalid ID") from None
        except IndexError:
            raise Exception("Handler does not exist") from None

    def get_active_listener(self, listener_id: int) -> Optional[BaseListener]:
        """Get a listener by id"""
        try:
            return self.active_listeners[str(listener_id)]
        except ValueError:
            raise Exception("Invalid ID.") from None
        except IndexError:
            raise Exception("Listener is not active.") from None

    def add_active_listener(self, listener: BaseListener):
        """Add a listener to the server"""
        self.active_listeners_count += 1
        self.active_listeners[str(listener.id)] = listener

    def add_active_handler(self, handler: BaseHandler):
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
