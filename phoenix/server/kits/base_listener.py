import time
from abc import abstractmethod
from typing import TYPE_CHECKING

from phoenix.server.database import ListenerModel, LogEntryModel, Session
from phoenix.server.utils.features import Feature
from phoenix.server.utils.options import OptionPool
from phoenix.server.utils.ui import log

from .base_handler import BaseHandler

# to enable type hinting without circular imports
if TYPE_CHECKING:
    from phoenix.server.commander import Commander


class BaseListener:
    """This is the base class for all listeners."""

    name: str = "BaseListener"
    description: str = "This is the base class for all listeners."
    author: str = "Unknown"
    # The supported OS for the listener
    os: list[str] = ["linux", "windows", "osx"]
    options = OptionPool()
    features: list[Feature] = []

    def __init__(self, commander: "Commander", db_entry: "ListenerModel"):
        self.address = db_entry.address
        self.port = db_entry.port
        self.ssl = db_entry.ssl
        self.commander: "Commander" = commander
        self.id: int = db_entry.id

    @property
    def db_entry(self) -> ListenerModel:
        return Session().query(ListenerModel).filter_by(id=self.id).first()

    @property
    def handlers(self) -> list[BaseHandler]:
        handlers = []
        for handler in self.commander.active_handlers.values():
            if handler.listener.db_entry == self.db_entry:
                handlers.append(handler)
        Session.remove()
        return handlers

    def add_handler(self, handler: BaseHandler):
        """Add a handler to the listener."""
        self.commander.add_active_handler(handler)

    def remove_handler(self, handler: BaseHandler):
        """Remove a handler from the listener."""
        self.commander.remove_active_handler(handler.id)

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

    def refresh_connections(self):
        """Check if the connections are still alive."""
        while self.db_entry.response_time > 0:
            if self.stopped:
                break
            time.sleep(self.db_entry.response_time)
            try:
                for handler in self.handlers:
                    if not handler.alive():
                        LogEntryModel.log(
                            "danger",
                            "devices",
                            f"Device '{handler.name}' disconnected.",
                        )
                        self.remove_handler(handler)
            except Exception as e:
                log(str(e), "danger")

    @abstractmethod
    def start(self):
        """Start the listener."""
        ...

    @abstractmethod
    def stop(self):
        """Stop the listener."""
        ...

    @classmethod
    def to_dict(cls, commander: "Commander") -> dict:
        """Return a dict with all options of the listener."""
        return {
            "name": cls.name,
            "description": cls.description,
            "os": cls.os,
            "options": cls.options.to_dict(commander),
        }
