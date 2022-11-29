"""The Devices Model"""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid1

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from phoenix_framework.server.commander import Commander

    from .listeners import ListenerModel
    from .stagers import StagerModel
    from .tasks import TaskModel


class DeviceModel(Base):
    """The Devices Model"""

    __tablename__ = "Devices"
    id: int = Column(Integer, primary_key=True, nullable=False)
    name: str = Column(String, unique=True, nullable=False)
    hostname: str = Column(String(100))
    address: str = Column(String(100), nullable=False)
    os: str = Column(String(10))
    architecture: str = Column(String(10))
    user: str = Column(String(100))
    admin: bool = Column(Boolean, default=False)
    infos: dict = Column(MutableDict.as_mutable(JSON), default={})
    connection_date: datetime = Column(DateTime)
    last_online: datetime = Column(DateTime)
    stager_id: int = Column(Integer, ForeignKey("Stagers.id"), nullable=False)
    stager: "StagerModel" = relationship("StagerModel", back_populates="devices")
    tasks: list["TaskModel"] = relationship("TaskModel", back_populates="device")

    @property
    def connected(self):
        return (datetime.now() - self.last_online).seconds < 10

    def to_dict(
        self,
        commander: "Commander",
        show_stager: bool = True,
        show_tasks: bool = True,
    ) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "hostname": self.hostname,
            "address": self.address,
            "os": self.os,
            "architecture": self.architecture,
            "user": self.user,
            "admin": self.admin,
            "infos": self.infos,
            "connection_date": self.connection_date,
            "last_online": self.last_online,
            "stager": self.stager.to_dict(commander, show_listener=False)
            if show_stager
            else self.stager.id,
            "tasks": [task.to_dict(commander, show_device=False) for task in self.tasks]
            if show_tasks
            else [task.id for task in self.tasks],
        }
        try:
            if commander is None:
                data["connected"] = "Unknown"
            else:
                commander.get_active_handler(self.id)
        except KeyError:
            data["connected"] = False
        else:
            data["connected"] = True
        return data

    @classmethod
    def generate_device(
        cls,
        stager: "StagerModel",
        hostname: str,
        address: str,
        os: str,
        architecture: str,
        user: str,
        admin: bool,
    ) -> "ListenerModel":
        return cls(
            name=str(uuid1()).split("-")[0],
            hostname=hostname,
            address=address,
            os=os,
            architecture=architecture,
            user=user,
            admin=admin,
            connection_date=datetime.now(),
            last_online=datetime.now(),
            stager=stager,
        )

    def delete(self, session):
        """Delete the device and all unfinished tasks"""
        session.delete(self)
        for task in self.tasks:
            if not task.finished:
                session.delete(task)
        session.commit()
