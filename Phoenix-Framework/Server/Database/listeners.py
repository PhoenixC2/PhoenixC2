"""The Listeners Model"""
import importlib
from typing import TYPE_CHECKING

from Creator.available import AVAILABLE_LISTENERS
from sqlalchemy import JSON, Boolean, Column, Integer, String
from sqlalchemy.orm import Session, relationship

from .base import Base

if TYPE_CHECKING:
    from Commander import Commander
    from Listeners.base import BaseListener
    from Utils.options import OptionPool

    from .devices import DeviceModel
    from .stagers import StagerModel


class ListenerModel(Base):
    """The Listeners Model"""
    __tablename__ = "Listeners"
    id: int = Column(
        Integer, primary_key=True, nullable=False)
    name: str = Column(String(100))
    type: str = Column(String(100))
    address: str = Column(String(15))
    port: int = Column(Integer)
    ssl: bool = Column(Boolean)
    connection_limit = Column(Integer, name="limit")
    options: dict = Column(JSON, default=[])
    stagers: list["StagerModel"] = relationship(
        "StagerModel",
        back_populates="listener")
    devices: list["DeviceModel"] = relationship(
        "DeviceModel",
        back_populates="listener"
    )

    def is_active(self, commander: "Commander"):
        """Returns True if listeners is active, else False"""
        try:
            commander.get_active_listener(self.id)
        except:
            return False
        else:
            return True

    def to_json(self, commander: "Commander", show_stagers: bool = True, show_devices: bool = True) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "address": self.address,
            "port": self.port,
            "ssl": self.ssl,
            "limit": self.connection_limit,
            "active": self.is_active(commander),
            "options": self.options,
            "stagers": [stager.to_json(commander, show_listener=False)
                        for stager in self.stagers] if show_stagers
            else [stager.id for stager in self.stagers],
            "devices": [device.to_json(commander, show_listener=False)
                        for device in self.devices] if show_devices
            else [device.id for device in self.devices]
        }

    def delete_stagers(self, db_session: Session):
        """Delete all stagers if listener is getting removed"""
        for stager in self.stagers:
            db_session.delete(stager)

    def get_listener_object(self, commander: "Commander") -> "BaseListener":
        """Create the Listener Object"""
        return importlib.import_module("Listeners." + self.type.replace("/", ".")).Listener(
            commander, self)

    def get_optionse(self) -> "OptionPool":
        """Get the options based on the listener type."""

        if self.type not in AVAILABLE_LISTENERS:
            raise ValueError(f"'{self.type}' isn't available.")

        try:
            open("Listeners/" + self.type + ".py", "r").close()
        except:
            raise Exception(f"Listener {self.type} does not exist") from None

        listener: "BaseListener" = importlib.import_module(
            "Listeners." + self.type.replace("/", ".")).Listener
        return listener.listener_pool

    @staticmethod
    def get_options_from_type(type: str) -> "OptionPool":
        """Get the options based on the listener type."""

        if type not in AVAILABLE_LISTENERS:
            raise ValueError(f"'{type}' isn't available.")

        try:
            open("Listeners/" + type + ".py", "r").close()
        except:
            raise Exception(f"Listener {type} does not exist") from None

        listener: "BaseListener" = importlib.import_module(
            "Listeners." + type.replace("/", ".")).Listener
        return listener.listener_pool

    @staticmethod
    def create_listener_from_data(data: dict):
        """Create the stager using listener validated data"""
        standard = []
        # gets standard values present in every listener and remove them to only leave options
        for st_value in ["name", "type", "address", "port", "ssl", "limit"]:
            standard.append(data.pop(st_value))
        return ListenerModel(
            name=standard[0],
            type=standard[1],
            address=standard[2],
            port=standard[3],
            ssl=standard[4],
            connection_limit=standard[5],
            options=data
        )
