import threading
from typing import TYPE_CHECKING
from cryptography.fernet import Fernet
from abc import abstractmethod
from Handlers.base import BaseHandler
from Database.listeners import ListenerModel
if TYPE_CHECKING:
    from Server.server_class import ServerClass

class BaseListener():
    """This is the Base Class for all Listeners"""

    def __init__(self, server: "ServerClass", config: dict, db_entry: ListenerModel):
        self.address = config["address"]
        self.port = config["port"]
        self.ssl = True if str(config["ssl"]).lower() == "true" else False
        self.server: "ServerClass" = server
        self.db_entry = db_entry
        self.id = db_entry.listener_id
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

    def decrypt(self, data, key) -> str:
        """Decrypt Data"""
        return Fernet(key).decrypt(data).decode()

    def encrypt(self, data: str, key: str) -> bytes:
        """Encrypt Data"""
        return Fernet(key).encrypt(data.encode())

    def add_handler(self, handler: BaseHandler):
        """Add a Handler to the Listener"""
        self.handlers[str(handler.id)] = handler
        self.server.add_active_handler(handler)

    def remove_handler(self, handler: BaseHandler):
        """Remove a Handler from the Listener"""
        self.handlers.pop(str(handler.id))
        self.server.remove_handler(handler)
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