"""The Listeners Model"""
import importlib
import time
from datetime import datetime
from random import randint
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from phoenixc2.server import AVAILABLE_KITS
from phoenixc2.server.database.base import Base
from phoenixc2.server.database.engine import Session
from phoenixc2.server.utils.misc import generate_name

from .operations import OperationModel

if TYPE_CHECKING:
    from phoenixc2.server.commander import Commander
    from phoenixc2.server.kits.base_listener import BaseListener

    from .stagers import StagerModel


class ListenerModel(Base):
    """The Listeners Model"""

    __tablename__ = "Listeners"

    id: int = Column(Integer, primary_key=True, nullable=False)
    name: str = Column(String(100), default=lambda: generate_name())
    type: str = Column(String(100))
    address: str = Column(String(15), default="0.0.0.0")
    port: int = Column(Integer, default=lambda: randint(1024, 65535))
    ssl: bool = Column(Boolean, default=True)
    enabled: bool = Column(Boolean, default=True)
    limit: int = Column(Integer, name="limit")
    response_time: int = Column(Integer, name="response_time", default=10)
    options: dict = Column(MutableDict.as_mutable(JSON), default={})
    created_at: datetime = Column(DateTime, default=datetime.now)
    updated_at: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    operation_id: int = Column(
        Integer,
        ForeignKey("Operations.id"),
        default=lambda: OperationModel.get_current_operation().id
        if OperationModel.get_current_operation() is not None
        else None,
    )
    operation: "OperationModel" = relationship(
        "OperationModel", back_populates="listeners"
    )
    stagers: list["StagerModel"] = relationship(
        "StagerModel", back_populates="listener", cascade="all, delete-orphan"
    )

    @property
    def listener_class(self) -> "BaseListener":
        """Get the listener class"""
        return self.get_class_from_type(self.type)

    @property
    def url(self) -> str:
        """Get the listener url"""
        return f"{self.listener_class.protocol}://{self.address}:{self.port}/"

    def is_active(self, commander: "Commander" = None) -> bool | str:
        """Returns True if listeners is active, else False"""
        try:
            if commander is None:
                return "Unknown"
            commander.get_active_listener(self.id)
        except KeyError:
            return False
        except TypeError:
            return False
        else:
            return True

    def to_dict(
        self,
        commander: "Commander",
        show_operation: bool = False,
        show_stagers: bool = False,
    ) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "address": self.address,
            "port": self.port,
            "ssl": self.ssl,
            "enabled": self.enabled,
            "limit": self.limit,
            "response_time": self.response_time,
            "active": self.is_active(commander),
            "options": self.options,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "stagers": [stager.to_dict(commander) for stager in self.stagers]
            if show_stagers
            else [stager.id for stager in self.stagers],
        }
        if self.operation is not None and show_operation:
            data["operation"] = self.operation.to_dict()
        else:
            data["operation"] = (
                self.operation.id if self.operation is not None else None
            )
        return data

    @staticmethod
    def get_class_from_type(type: str) -> "BaseListener":
        """Get the listener class based on its type"""
        type = type.replace("-", "_")
        if type not in AVAILABLE_KITS:
            raise ValueError(f"Listener '{type}' isn't available.")
        try:
            listener = importlib.import_module(
                "phoenixc2.server.kits." + type + ".listener"
            ).Listener
        except ModuleNotFoundError as e:
            raise FileNotFoundError(f"Stager '{type}' doesn't exist.") from e
        else:
            return listener

    @staticmethod
    def get_all_classes() -> list["BaseListener"]:
        """Get all listener classes."""
        return [
            ListenerModel.get_class_from_type(listener) for listener in AVAILABLE_KITS
        ]

    def start(self, commander: "Commander") -> str:
        """Start the listener"""
        listener_obj = self.create_object(commander)
        listener_obj.start()
        commander.add_active_listener(listener_obj)
        return f"Started listener '{self.name}' ({self.type}) on {self.address}:{self.port} ({self.id})"

    def stop(self, commander: "Commander"):
        """Stop the listener"""
        if self.is_active(commander):
            listener_obj = commander.get_active_listener(self.id)
            listener_obj.stop()
            commander.remove_active_listener(self.id)
        else:
            raise ValueError(f"Listener '{self.name}' isn't active.")

    def restart(self, commander: "Commander"):
        """Restart the listener"""
        self.stop(commander)
        time.sleep(2)
        self.start(commander)

    def delete_stagers(self):
        """Delete all stagers"""
        for stager in self.stagers:
            Session.delete(stager)

    def edit(self, data: dict):
        """Edit the listener"""
        options = self.listener_class.options
        
        data = options.validate_all(data)
        for key, value in data.items():
            option = options.get_option(key)
            if not option.editable:
                raise ValueError(f"Option '{key}' is not editable.")
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.options[key] = value

    def delete(self, stop: bool, commander: "Commander"):
        """Delete the listener"""
        if stop and self.is_active(commander):
            self.stop(commander)
        self.delete_stagers()
        Session.delete(self)

    def create_object(self, commander: "Commander") -> "BaseListener":
        """Create the Listener Object"""
        return self.listener_class(commander, self)

    @classmethod
    def create_from_data(cls, data: dict):
        """Create the stager using listener validated data"""
        return cls(
            name=data.pop("name"),
            type=data.pop("type"),
            address=data.pop("address"),
            port=data.pop("port"),
            ssl=data.pop("ssl"),
            enabled=data.pop("enabled"),
            limit=data.pop("limit"),
            response_time=data.pop("response_time"),
            options=data,
        )
