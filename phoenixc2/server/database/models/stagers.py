"""The Stagers Model"""
import importlib
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask import escape
from phoenixc2.server.kits import get_all_kits
from phoenixc2.server.database.base import Base
from phoenixc2.server.database.engine import Session
from phoenixc2.server.utils.resources import get_resource

from .operations import OperationModel

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander
    from phoenixc2.server.kits.stager_base import BasePayload, BaseStager, FinalPayload

    from .devices import DeviceModel
    from .listeners import ListenerModel


class StagerModel(Base):
    """The Stagers Model"""

    __mapper_args__ = {
        "confirm_deleted_rows": False
    }  # needed to avoid error bc of cascade delete
    __tablename__ = "Stagers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100))
    payload: Mapped[str] = mapped_column(String(100))
    retries: Mapped[int] = mapped_column(Integer)
    delay: Mapped[int] = mapped_column(Integer)
    different_address: Mapped[str] = mapped_column(String(100))
    options: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSON), default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
    listener_id: Mapped[int] = mapped_column(Integer, ForeignKey("Listeners.id"))
    listener: Mapped["ListenerModel"] = relationship(
        "ListenerModel", back_populates="stagers"
    )
    devices: Mapped[List["DeviceModel"]] = relationship(
        "DeviceModel", back_populates="stager", cascade="all, delete-orphan"
    )

    @property
    def operation(self) -> "OperationModel":
        """Returns the operation of the stager."""
        return self.listener.operation

    @property
    def stager_class(self) -> "BaseStager":
        """Returns the stager class."""
        return self.get_class_from_type(self.listener.type)

    @property
    def payload_class(self) -> "BasePayload":
        """Returns the payload class."""
        return self.stager_class.payloads[self.payload]

    def to_dict(
        self,
        commander: "Commander",
        show_listener: bool = False,
        show_devices: bool = False,
    ) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "payload": self.payload,
            "retries": self.retries,
            "delay": self.delay,
            "different_address": self.different_address,
            "options": self.options,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "listener": self.listener.to_dict(commander)
            if show_listener
            else self.listener.id,
            "devices": [
                device.to_dict(commander, show_stager=False) for device in self.devices
            ]
            if show_devices
            else [device.id for device in self.devices],
        }

    def edit(self, data: dict[str, any]):
        """Edit the stager"""
        options = self.stager_class.option_pool

        # get options from payload class
        options.extend(self.payload_class.option_pool)

        for key, value in data.items():
            option = options.get_option(key)

            value = option.validate_data(value)
            if not option.editable:
                raise ValueError(f"Option '{key}' is not editable.")

            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.options[key] = value

    def delete(self):
        """Delete the stager and its generated payloads."""
        Session.delete(self)
        # delete all payloads who start with the stager name
        for payload in get_resource("data", "stagers").glob(f"{self.name}*"):
            payload.unlink()

    def generate_payload(self, recompile: bool = False) -> "FinalPayload":
        """Generate the payload"""
        return self.stager_class.generate(self, recompile)

    @staticmethod
    def get_class_from_type(type: str) -> "BaseStager":
        """Return the stager class based on its type."""
        type = escape(type.replace("-", "_"))
        if type not in get_all_kits():
            raise ValueError(f"Stager '{type}' isn't installed.")
        try:
            stager = importlib.import_module(
                "phoenixc2.server.kits." + type.replace("-", "_") + ".stager"
            ).Stager()
        except ModuleNotFoundError as e:
            raise FileNotFoundError(f"Stager '{type}' doesn't exist.") from e
        else:
            return stager

    @staticmethod
    def get_all_classes() -> list["BaseStager"]:
        """Get all stager classes."""
        return [StagerModel.get_class_from_type(stager) for stager in get_all_kits()]

    @classmethod
    def create_from_data(cls, data: dict):
        """Create the stager using custom validated data"""
        standard = []
        # gets standard keys and store the rest in options
        for st_value in [
            "name",
            "listener",
            "payload",
            "retries",
            "delay",
            "different_address",
        ]:
            standard.append(data.pop(st_value))
        return cls(
            name=standard[0],
            listener=standard[1],
            payload=standard[2],
            retries=standard[3],
            delay=standard[4],
            different_address=standard[5],
            options=data,
        )

    def __repr__(self) -> str:
        return (
            f"<StagerModel(id={self.id}, name={self.name},"
            f"listener={self.listener.name}, payload={self.payload})>"
        )
