import threading
from typing import TYPE_CHECKING
from cryptography.fernet import Fernet
from abc import abstractmethod
from Handlers.base import BaseHandler


# to enable type hinting without circular imports
if TYPE_CHECKING:
    from Database.listeners import ListenerModel
    from Server.server_class import ServerClass


class BaseListener():
    """This is the Base Class for all Listeners"""

    def __init__(self, server: "ServerClass", db_entry: "ListenerModel"):
        self.address = db_entry.address
        self.port = db_entry.port
        self.ssl = db_entry.ssl
        self.server: "ServerClass" = server
        self.db_entry: "ListenerModel" = db_entry
        self.id: int = db_entry.listener_id
        self.handlers: dict[str, BaseHandler] = {}
        self.stopped = False
        self.listener_thread: threading.Thread
        self.refresher_thread: threading.Thread

    def status(self) -> tuple[bool, bool, bool]:
        """Get Status of the Server

        Returns:
            bool: True if socket is running, False if not
            bool: True if listener is running, False if not
            bool: True if refresher is running, False if not"""
        return self.stopped, self.listener_thread.is_alive(), self.refresher_thread.is_alive()

    def decrypt(self, data: str, key: bytes) -> str:
        """Decrypt Data"""
        return Fernet(key).decrypt(data).decode()

    def encrypt(self, data: str, key: bytes) -> bytes:
        """Encrypt Data"""
        return Fernet(key).encrypt(data.encode())

    def add_handler(self, handler: BaseHandler):
        """Add a Handler to the Listener"""
        self.handlers[str(handler.id)] = handler
        self.server.add_active_handler(handler)

    def remove_handler(self, handler: BaseHandler):
        """Remove a Handler from the Listener"""
        self.handlers.pop(str(handler.id))
        self.server.remove_handler(handler.id)

    @abstractmethod
    def refresh_connections(self):
        """Check if the connections are still alive"""
        ...

    @abstractmethod
    def listen(self):
        """Listen for Connections"""
        ...

    @abstractmethod
    def start(self):
        """Start the Listener"""
        ...

    @abstractmethod
    def stop(self):
        """Stop the Listener"""
        ...
