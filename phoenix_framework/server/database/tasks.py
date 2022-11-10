"""The Tasks Model"""
import base64
import os
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid1

from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Session, relationship
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from phoenix_framework.server.utils.resources import get_resource

from .base import Base
from .devices import DeviceModel
from .logs import LogEntryModel

if TYPE_CHECKING:
    from phoenix_framework.server.commander import Commander


class TaskModel(Base):
    """The Tasks Model."""

    __tablename__ = "Tasks"
    id: int = Column(Integer, primary_key=True, nullable=False)
    name: str = Column(String(10), unique=True)
    description: str = Column(Text)
    device_id: int = Column(Integer, ForeignKey("Devices.id"))
    device: "DeviceModel" = relationship("DeviceModel", back_populates="tasks")
    type: str = Column(String(10), nullable=False)
    args: dict[str, any] = Column(MutableDict.as_mutable(JSON), default={})
    created_at: datetime = Column(DateTime)
    finished_at: datetime = Column(DateTime)
    success: bool = Column(Boolean)  # success | error
    output: str = Column(Text)

    @property
    def finished(self) -> bool:
        return self.finished_at is not None

    def to_dict(self, commander: "Commander", show_device: bool = True) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "device": self.device.to_dict(commander, show_tasks=False)
            if show_device and self.device is not None
            else self.device_id,
            "type": self.type,
            "args": self.args,
            "created_at": self.created_at,
            "finished_at": self.finished_at,
            "success": self.success,
            "output": self.output,
        }

    def finish(self, output: str, success: bool, session: Session):
        """Update the Task to be finished.
        Still has to be committed!"""
        if self.type == "download" and success:
            file_name = secure_filename(self.args["target_path"].split("/")[-1])
            # save file to downloads folder
            with get_resource("data/downloads/" + file_name).open("wb") as f:
                f.write(base64.b64decode(output))
            self.output = file_name  # file can then be found using the api
        else:
            self.output = output
        self.success = success
        self.finished_at = datetime.now()
        if success:
            LogEntryModel.log(
                "success",
                "devices",
                f"Task '{self.name}' finished successfully",
                session,
            )
        else:
            LogEntryModel.log(
                "danger",
                "devices",
                f"Task '{self.name}' finished with an error",
                session,
            )

    @staticmethod
    def generate_task(device_or_id: DeviceModel | int | str) -> "TaskModel":
        task = TaskModel(
            name=str(uuid1()).split("-")[0], created_at=datetime.now(), args={}
        )
        if type(device_or_id) == DeviceModel:
            task.device = device_or_id
        elif type(device_or_id) == int:
            task.device_id = device_or_id
        elif type(device_or_id) == str:
            task.device_id = int(device_or_id)
        else:
            raise TypeError("Invalid Type for device.")
        return task

    """ default methods for every stager """

    @staticmethod
    def upload(
        device_or_id: DeviceModel | int, file: FileStorage, target_path: str
    ) -> "TaskModel":
        """Create a Upload task.

        Args:
        -----
            device (DeviceModel): The device to execute the task
            file (io.TextIOWrapper): The file object
            target_path (str): The path where the file should be saved
        """
        if target_path is None:
            raise TypeError("File path is missing.")
        file.save(os.path.join("Data", "Uploads", secure_filename(file.name)))
        task = TaskModel.generate_task(device_or_id)
        task.type = "upload"
        task.args["file_name"] = secure_filename(file.name)
        task.args["target_path"] = target_path
        return task

    @staticmethod
    def download(device_or_id: DeviceModel | int, target_path: str) -> "TaskModel":
        """Create a Download task.

        Args:
        -----
            device (DeviceModel): the device to execute the task
            target_path (str): The path of the file too download
        """
        task = TaskModel.generate_task(device_or_id)
        task.type = "download"
        task.args["target_path"] = target_path
        return task

    @staticmethod
    def reverse_shell(
        device_or_id: DeviceModel | int, address: str, port: int
    ) -> "TaskModel":
        """Create a Reverse-Shell task , executed using netcat.

        Args:
        -----
            device (DeviceModel): the device to execute the task
            address (str): The listening address
            port (int): The listening port
            binary (str): The binary to execute
        """
        task = TaskModel.generate_task(device_or_id)
        task.type = "reverse-shell"
        task.args["address"] = address
        task.args["port"] = port
        return task

    @staticmethod
    def remote_command_execution(
        device_or_id: DeviceModel | int, cmd: str
    ) -> "TaskModel":
        """Create a Remote-Command-Execution task.

        Args:
        -----
            device (DeviceModel): the device to execute the task
            cmd (str): Command to execute
        """
        task = TaskModel.generate_task(device_or_id)
        task.type = "rce"
        task.args["cmd"] = cmd
        return task

    @staticmethod
    def list_directory_contents(
        device_or_id: DeviceModel | int, dir: str
    ) -> "TaskModel":
        """Create a List-Directory-Contents task.

        Args:
        -----
            device (DeviceModel): the device to execute the task
            dir (str): Path to the dir which should be listed
        """
        task = TaskModel.generate_task(device_or_id)
        task.type = "dir"
        task.args["dir"] = dir
        return task
