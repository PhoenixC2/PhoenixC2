"""This is the C2 commander Class which handles the devices & listeners"""
from typing import Optional

from phoenix_framework.server.kits.base_handler import BaseHandler
from phoenix_framework.server.kits.base_listener import BaseListener
from phoenix_framework.server.utils.web import FlaskThread

INVALID_ID = "Invalid ID"
HANDLER_DOES_NOT_EXIST = "Handler doesn't exist"
LISTENER_DOES_NOT_EXIST = "Listener doesn't exist"


class Commander:
    """This is the Commander which handles the devices & listeners"""

    def __init__(self):
        self.web_server: FlaskThread
        self.active_listeners: dict[int, BaseListener] = {}
        self.active_handlers: dict[int, BaseHandler] = {}

    def get_active_handler(self, handler_id: int) -> Optional[BaseHandler]:
        """Get a handler by id"""
        try:
            return self.active_handlers[int(handler_id)]
        except ValueError as e:
            raise ValueError(INVALID_ID) from e
        except KeyError as e:
            raise KeyError(HANDLER_DOES_NOT_EXIST) from e

    def get_active_listener(self, listener_id: int) -> Optional[BaseListener]:
        """Get a listener by id"""
        try:
            return self.active_listeners[int(listener_id)]
        except ValueError as e:
            raise ValueError(INVALID_ID) from e
        except KeyError:
            raise KeyError(LISTENER_DOES_NOT_EXIST) from None

    def add_active_listener(self, listener: BaseListener):
        """Add a listener to the commander"""
        self.active_listeners[int(listener.id)] = listener

    def add_active_handler(self, handler: BaseHandler):
        """Add a handler to the commander"""
        self.active_handlers[int(handler.id)] = handler

    def remove_active_listener(self, listener_id: int):
        """Remove a listener from the commander"""
        try:
            self.active_listeners.pop(int(listener_id))
        except ValueError as e:
            raise ValueError(INVALID_ID) from e
        except KeyError as e:
            raise KeyError(LISTENER_DOES_NOT_EXIST) from e

    def remove_active_handler(self, handler_id: int):
        """Remove a device from the commander by id"""
        try:
            self.active_handlers.pop(int(handler_id))
        except ValueError as e:
            raise ValueError(INVALID_ID) from e
        except KeyError as e:
            raise KeyError(HANDLER_DOES_NOT_EXIST) from e
