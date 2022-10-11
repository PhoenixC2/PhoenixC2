"""The Stagers Model"""
import importlib
from typing import TYPE_CHECKING

from Creator.available import AVAILABLE_KITS
from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship

from .base import Base

if TYPE_CHECKING:
    from Commander import Commander
    from Server.Kits.base_listener import BaseListener
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

    def to_dict(self, commander: "Commander", show_listener: bool = True) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "listener": self.listener.to_dict(commander, show_stagers=False) if show_listener else self.listener.id,
            "encoding": self.encoding,
            "random_size": self.random_size,
            "timeout": self.timeout,
            "format": self.format,
            "delay": self.delay
        }

    def get_options(self) -> "OptionPool":
        """Get the options based on the stager type."""
        if self.listener.type not in AVAILABLE_PAYLOADS:
            raise ValueError(f"'{self.listener.type}' isn't available.")

        try:
            open("Kits/" + self.listener.type + "/stager.py", "r").close()
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Stager {self.listener.type} does not exist") from e

        return importlib.import_module("Kits." + self.type + ".stager").Stager.option_pool

    @staticmethod
    def get_options_from_type(type: str) -> "OptionPool":
        """Get the options based on the stager type."""

        if type not in AVAILABLE_KITS:
            raise ValueError(f"'{type}' isn't available.")

        try:
            open("Kits/" + type + "/stager.py", "r").close()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Stager {type} does not exist") from e

        return importlib.import_module("Kits." + type + ".stager").Stager.option_pool
    
    def edit(self, session: Session, data: dict):
        """Edit the listener"""
        for key, value in data.items():
            if not hasattr(self, key):
                if key in self.options:
                    self.options[key] = value
            else:
                setattr(self, key, value)
        session.commit()
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
