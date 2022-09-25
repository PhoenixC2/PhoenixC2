import threading
from abc import abstractmethod
from typing import TYPE_CHECKING

from Database import Session
from Database.listeners import ListenerModel
from Handlers.base import BaseHandler
from Utils.options import OptionPool

# to enable type hinting without circular imports
if TYPE_CHECKING:
    from Commander import Commander



class BaseListener():
    """This is the Base Class for all Listeners."""
    listener_pool = OptionPool()
    stager_pool = OptionPool()
    def __init__(self, commander: "Commander", db_entry: "ListenerModel"):
        self.address = db_entry.address
        self.port = db_entry.port
        self.ssl = db_entry.ssl
        self.commander: "Commander" = commander
        self.id: int = db_entry.id
    @property
    def db_entry(self):
        return Session().query(ListenerModel).filter_by(id=self.id).first()
    @property
    def handlers(self):
        Session 
        handlers = []
        for handler in self.commander.active_handlers.values():
            if handler.db_entry.listener == self.db_entry:
                handlers.append(handler)
        Session.remove()
        return handlers
    def status(self) -> True:
        """Get status of the listener.

        Returns:
            bool: True if listener is running, False if not"""
        ...

    def add_handler(self, handler: BaseHandler):
        """Add a Handler to the Listener"""
        self.commander.add_active_handler(handler)

    def remove_handler(self, handler: BaseHandler):
        """Remove a Handler from the Listener"""
        self.commander.remove_handler(handler.id)

    def get_handler(self, id_or_name:int|str) -> BaseHandler | None:
        """Return a handler based on its id or name."""
        if type(id_or_name) == int:
            for handler in self.handlers:
                if handler.id == id_or_name:
                    return handler
        else:
            for handler in self.handlers:
                if handler.name == id_or_name:
                    return handler
    @abstractmethod
    def refresh_connections(self):
        """Check if the connections are still alive."""
        ...

    @abstractmethod
    def start(self):
        """Start the Listener."""
        ...

    @abstractmethod
    def stop(self):
        """Stop the Listener."""
        ...
