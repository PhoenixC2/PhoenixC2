"""The Tasks Model"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from Commander import Commander

    from .devices import DeviceModel


class TasksModel(Base):
    """The Tasks Model"""
    __tablename__ = "Tasks"
    id: int = Column(Integer, primary_key=True,
                     nullable=False)
    name: str = Column(String(10), unique=True)
    device_id: int = Column(Integer, ForeignKey("Devices.id"))
    device: "DeviceModel" = relationship(
        "DeviceModel", back_populates="tasks"
    )
    type: str = Column(String(10))
    args: list[str] = Column(JSON, default=[])
    created_at: datetime = Column(DateTime)
    finished_at: datetime = Column(DateTime)
    output: str = Text()

    def to_json(self, commander: "Commander", show_device: bool = True) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "device": self.device.to_json(commander, show_tasks=False) if show_device else self.device.id,
            "type": self.type,
            "args": self.args,
            "created_at": self.created_at,
            "finished_at": self.finished_at
        }

    def finish(self, output: str):
        """Update the Task to be finished"""
        self.output = output
        self.finished_at = datetime.now()
        