"""The Devices Model"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base
from .credentials import CredentialModel

if TYPE_CHECKING:
    from Commander import Commander

    from .listeners import ListenerModel
    from .tasks import TaskModel


class DeviceModel(Base):
    """The Devices Model"""
    __tablename__ = "Devices"
    id: int = Column(Integer, primary_key=True, nullable=False)
    name: str = Column(String, unique=True, nullable=False)
    hostname: str = Column(String(100))
    address: str = Column(String(100), nullable=False)
    connection_date: datetime = Column(DateTime)
    last_online: datetime = Column(DateTime)
    listener_id: int = Column(Integer, ForeignKey("Listeners.id"))
    listener: "ListenerModel" = relationship(
        "ListenerModel", back_populates="devices")
    tasks: list["TaskModel"] = relationship(
        "TaskModel",
        back_populates="device")
    @property
    def connected(self):
        delta = (datetime.now() - self.last_online).seconds
        if delta < 10:
            return True
        return False
    
    def to_json(self, commander: "Commander", show_listener: bool = True, show_tasks: bool = True) -> dict:
        data = {
            "id": self.id,
            "hostname": self.hostname,
            "address": self.address,
            "connection_date": self.connection_date,
            "last_online": self.last_online,
            "listener": self.listener.to_json(commander, show_devices=False) if show_listener else self.listener_id,
            "tasks": [task.to_json(commander, show_device=False)
                      for task in self.tasks] if show_tasks
            else [task.id for task in self.tasks]
        }
        try:
            commander.get_active_handler(self.id)
        except:
            data["connected"] = False
        else:
            data["connected"] = True
        return data

