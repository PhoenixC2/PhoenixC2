import time
from abc import abstractmethod
from typing import TYPE_CHECKING

from Database import Session, ListenerModel, LogEntryModel
from Utils.options import OptionPool
from Utils.ui import log

from .base_handler import BaseHandler

# to enable type hinting without circular imports
if TYPE_CHECKING:
    from Commander import Commander


class BaseListener():
    """This is the Base Class for all Listeners."""
    name: str = "BaseListener"
    description: str = "This is the Base Class for all Listeners."
    author: str = "Unknown"
    # The supported OS for the listener
    os: list[str] = ["linux", "windows", "osx"]
    options = OptionPool()

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
    def handlers(self) -> list[BaseHandler]:
        handlers = []
        for handler in self.commander.active_handlers.values():
            if handler.db_entry.listener == self.db_entry:
                handlers.append(handler)
        Session.remove()
        return handlers

    def add_handler(self, handler: BaseHandler):
        """Add a Handler to the Listener"""
        self.commander.add_active_handler(handler)

    def remove_handler(self, handler: BaseHandler):
        """Remove a Handler from the Listener"""
        self.commander.remove_handler(handler.id)

    def get_handler(self, id_or_name: int | str) -> BaseHandler | None:
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
    def status(self) -> bool:
        """Get status of the listener.

        Returns:
            bool: True if listener is running, False if not"""
        ...

    @abstractmethod
    def refresh_connections(self):
        """Check if the connections are still alive."""
        while True:
            if self.stopped:
                break
            time.sleep(5)
            try:
                for handler in self.handlers:
                    if not handler.alive():
                        LogEntryModel.log("danger", "devices", f"Device '{handler.name}' disconnected.", Session)
                        self.remove_handler(handler)
            except Exception as e:
                log(str(e), "danger")

    @abstractmethod
    def start(self):
        """Start the Listener."""
        ...

    @abstractmethod
    def stop(self):
        """Stop the Listener."""
        ...

    @classmethod
    def to_dict(cls, commander: "Commander") -> dict:
        """Return a dict with all options of the Listener."""
        return {
            "name": cls.name,
            "description": cls.description,
            "os": cls.os,
            "options": cls.options.to_dict(commander)
        }
