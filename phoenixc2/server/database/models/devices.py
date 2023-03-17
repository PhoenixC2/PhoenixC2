"""The Devices Model"""
from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import uuid1

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from phoenixc2.server.database.base import Base
from phoenixc2.server.database.engine import Session

from .operations import OperationModel

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander

    from .listeners import ListenerModel
    from .stagers import StagerModel
    from .tasks import TaskModel


class DeviceModel(Base):
    """The Devices Model"""

    __mapper_args__ = {
        "confirm_deleted_rows": False
    }  # needed to avoid error bc of cascade delete
    __tablename__ = "Devices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        String, default=lambda: str(uuid1()).split("-")[0], unique=True
    )
    hostname: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(100))
    os: Mapped[str] = mapped_column(String(10))
    architecture: Mapped[str] = mapped_column(String(10))
    user: Mapped[str] = mapped_column(String(100))
    admin: Mapped[bool] = mapped_column(Boolean, default=False)
    connection_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_online: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    stager_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("Stagers.id"), nullable=False
    )
    stager: Mapped["StagerModel"] = relationship(
        "StagerModel", back_populates="devices"
    )
    tasks: Mapped[List["TaskModel"]] = relationship(
        "TaskModel", back_populates="device"
    )

    @property
    def operation(self) -> "OperationModel":
        return self.stager.operation

    @property
    def connected(self) -> bool:
        """Check if the device is connected"""
        return (datetime.now() - self.last_online).seconds < 10

    def to_dict(
        self,
        commander: "Commander",
        show_stager: bool = False,
        show_operation: bool = False,
        show_tasks: bool = False,
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
            "connection_time": self.connection_time,
            "last_online": self.last_online,
            "stager": self.stager.to_dict(commander) if show_stager else self.stager.id,
            "tasks": [task.to_dict(commander) for task in self.tasks]
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

        if self.operation is not None and show_operation:
            data["operation"] = self.operation.to_dict()
        else:
            data["operation"] = (
                self.operation.id if self.operation is not None else None
            )

        return data

    def delete(self):
        """Delete the device and all unfinished tasks"""
        Session.delete(self)
        for task in self.tasks:
            if not task.finished:
                Session.delete(task)

    @classmethod
    def register(
        cls,
        hostname: str,
        address: str,
        os: str,
        architecture: str,
        user: str,
        admin: bool,
        stager: "StagerModel",
    ) -> "ListenerModel":
        return cls(
            hostname=hostname,
            address=address,
            os=os,
            architecture=architecture,
            user=user,
            admin=admin,
            stager=stager,
        )
