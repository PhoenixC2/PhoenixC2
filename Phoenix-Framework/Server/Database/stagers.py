"""The Stagers Model"""
import importlib
from typing import TYPE_CHECKING

from Creator.available import AVAILABLE_STAGERS
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from Commander import Commander
    from Listeners.base import BaseListener
    from Utils.options import OptionPool

    from .listeners import ListenerModel


class StagerModel(Base):
    """The Stagers Model"""
    __tablename__ = "Stagers"
    id: int = Column(Integer, primary_key=True, nullable=False)
    name: str = Column(String(100))
    listener_id: int = Column(Integer, ForeignKey("Listeners.id"))
    listener: "ListenerModel" = relationship(
        "ListenerModel", back_populates="stagers")
    encoding: str = Column(String(10))
    random_size: bool = Column(Boolean)
    timeout: int = Column(Integer)
    format: str = Column(String(10))
    delay: int = Column(Integer)
    options: dict = Column(JSON)

    def to_json(self, commander: "Commander", show_listener: bool = True) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "listener": self.listener.to_json(commander, show_stagers=False) if show_listener else self.listener.id,
            "encoding": self.encoding,
            "random_size": self.random_size,
            "timeout": self.timeout,
            "format": self.format,
            "delay": self.delay
        }

    def get_options(self) -> "OptionPool":
        """Get the options based on the listener type."""

        if self.listener.type not in AVAILABLE_STAGERS:
            raise ValueError(f"'{self.listener.type}' isn't available.")

        try:
            open("Payloads/" + self.listener.type + ".py", "r").close()
        except:
            raise Exception(
                f"Stager {self.listener.type} does not exist") from None

        listener: "BaseListener" = importlib.import_module(
            "Listeners." + self.listener.type.replace("/", ".")).Listener
        return listener.stager_pool

    @staticmethod
    def get_options_from_type(type: str) -> "OptionPool":
        """Get the options based on the listener type."""

        if type not in AVAILABLE_STAGERS:
            raise ValueError(f"'{type}' isn't available.")

        try:
            open("Payloads/" + type + ".py", "r").close()
        except:
            raise Exception(f"Stager {type} does not exist") from None

        listener: "BaseListener" = importlib.import_module(
            "Listeners." + type.replace("/", ".")).Listener
        return listener.stager_pool

    @staticmethod
    def create_stager_from_data(data: dict):
        """Create the stager using custom validated data"""
        standard = []
        # gets standard values present in every stager and remove them to only leave options
        for st_value in ["name", "listener", "encoding", "random_size", "timeout", "format", "delay"]:
            standard.append(data.pop(st_value))
        return StagerModel(
            name=standard[0],
            listener=standard[1],
            encoding=standard[2],
            random_size=standard[3],
            timeout=standard[4],
            format=standard[5],
            delay=standard[6],
            options=data
        )
