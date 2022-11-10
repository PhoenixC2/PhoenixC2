"""The Listeners Model"""
import importlib
import json
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, Column, Integer, String
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Session, relationship

from phoenix_framework.server.creator.available import AVAILABLE_KITS
from phoenix_framework.server.utils.resources import get_resource

from .base import Base

if TYPE_CHECKING:
    from phoenix_framework.server.commander import Commander
    from phoenix_framework.server.kits.base_listener import BaseListener
    from phoenix_framework.server.utils.options import OptionPool

    from .devices import DeviceModel
    from .stagers import StagerModel


class ListenerModel(Base):
    """The Listeners Model"""

    __tablename__ = "Listeners"
    id: int = Column(Integer, primary_key=True, nullable=False)
    name: str = Column(String(100))
    type: str = Column(String(100))
    address: str = Column(String(15))
    port: int = Column(Integer)
    ssl: bool = Column(Boolean)
    enabled: bool = Column(Boolean, default=True)
    limit = Column(Integer, name="limit")
    options: dict = Column(MutableDict.as_mutable(JSON), default=[])
    stagers: list["StagerModel"] = relationship(
        "StagerModel", back_populates="listener"
    )
    devices: list["DeviceModel"] = relationship(
        "DeviceModel", back_populates="listener"
    )

    @property
    def listener_class(self) -> "BaseListener":
        """Get the listener class"""
        return self.get_listener_class_from_type(self.type)

    def is_active(self, commander: "Commander" = None) -> bool | str:
        """Returns True if listeners is active, else False"""
        try:
            if commander is None:
                return "Unknown"
            commander.get_active_listener(self.id)
        except KeyError:
            return False
        else:
            return True

    def to_dict(
        self,
        commander: "Commander",
        show_stagers: bool = True,
        show_devices: bool = True,
    ) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "address": self.address,
            "port": self.port,
            "ssl": self.ssl,
            "enabled": self.enabled,
            "limit": self.limit,
            "active": self.is_active(commander),
            "options": self.options,
            "stagers": [
                stager.to_dict(commander, show_listener=False)
                for stager in self.stagers
            ]
            if show_stagers
            else [stager.id for stager in self.stagers],
            "devices": [
                device.to_dict(commander, show_listener=False)
                for device in self.devices
            ]
            if show_devices
            else [device.id for device in self.devices],
        }

    def to_json(
        self,
        commander: "Commander",
        show_stagers: bool = True,
        show_devices: bool = True,
    ) -> str:
        """Return a JSON string"""
        return json.dumps(self.to_dict(commander, show_stagers, show_devices))

    @staticmethod
    def get_listener_class_from_type(type: str) -> "BaseListener":
        """Get the listener class based on its type"""
        type = type.replace("-", "_")
        if type not in AVAILABLE_KITS:
            raise ValueError(f"Listener '{type}' isn't available.")
        try:
            listener = importlib.import_module(
                "phoenix_framework.server.kits." + type + ".listener"
            ).Listener
        except ModuleNotFoundError as e:
            raise FileNotFoundError(f"Stager '{type}' doesn't exist.") from e
        else:
            return listener

    @staticmethod
    def get_all_listener_classes() -> list["BaseListener"]:
        """Get all listener classes."""
        return [
            ListenerModel.get_listener_class_from_type(listener)
            for listener in AVAILABLE_KITS
        ]

    def delete_stagers(self, session: Session):
        """Delete all stagers"""
        for stager in self.stagers:
            session.delete(stager)

    def edit(self, data: dict):
        """Edit the listener"""
        options = (
            self.listener_class.options
        )  # so we dont have to get the class multiple times
        for key, value in data.items():
            if hasattr(self, key):
                if value == str(getattr(self, key)):
                    continue
                option = options.get_option(key)
                if not option.editable:
                    raise ValueError(f"Option '{key}' is not editable.")
                value = option.validate_data(value)
                setattr(self, key, value)
            else:
                if key in self.options:
                    if value == self.options[key]:
                        continue
                    option = options.get_option(key)
                    if not option.editable:
                        raise ValueError(f"Option '{key}' is not editable.")
                    value = option.validate_data(value)
                    self.options[key] = value
                else:
                    raise KeyError(f"{key} is not a valid key")

    def create_listener_object(self, commander: "Commander") -> "BaseListener":
        """Create the Listener Object"""
        return self.listener_class(commander, self)

    @classmethod
    def create_listener_from_data(cls, data: dict):
        """Create the stager using listener validated data"""
        standard = []
        # gets standard values present in every listener and remove them to only leave options
        for st_value in ["name", "type", "address", "port", "ssl", "limit", "enabled"]:
            standard.append(data.pop(st_value))
        return cls(
            name=standard[0],
            type=standard[1],
            address=standard[2],
            port=standard[3],
            ssl=standard[4],
            limit=standard[5],
            enabled=standard[6],
            options=data,
        )