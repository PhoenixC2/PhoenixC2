"""The Tasks Model"""
import base64
import os
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid1

from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from phoenix.server.modules import get_module
from phoenix.server.utils.resources import get_resource

from .base import Base
from .engine import Session
from .devices import DeviceModel
from .logs import LogEntryModel

if TYPE_CHECKING:
    from phoenix.server.commander import Commander


class TaskModel(Base):
    """The Tasks Model."""

    __tablename__ = "Tasks"
    id: int = Column(Integer, primary_key=True, nullable=False)
    name: str = Column(
        String(10), unique=True, default=lambda: str(uuid1()).split("-")[0]
    )
    description: str = Column(Text)
    type: str = Column(String(10), nullable=False)
    args: dict[str, any] = Column(MutableDict.as_mutable(JSON), default=dict)
    success: bool = Column(Boolean)  # success | error
    output: str = Column(Text)
    created_at: datetime = Column(DateTime, default=datetime.now)
    finished_at: datetime = Column(DateTime, onupdate=datetime.now)
    device_id: int = Column(Integer, ForeignKey("Devices.id"))
    device: "DeviceModel" = relationship("DeviceModel", back_populates="tasks")

    @property
    def finished(self) -> bool:
        return self.finished_at is not None

    def to_dict(self, commander: "Commander", show_device: bool = False) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "args": self.args,
            "success": self.success,
            "created_at": self.created_at,
            "finished_at": self.finished_at,
            "output": self.output,
            "device": self.device.to_dict(commander)
            if show_device and self.device is not None
            else self.device_id,
        }

    def finish(self, output: str, success: bool):
        """Update the Task to be finished.
        Still has to be committed!"""
        if self.type == "download" and success:
            file_name = secure_filename(self.args["target_path"].split("/")[-1])
            # save file to downloads folder
            with get_resource("data/downloads/", file_name, skip_file_check=True).open(
                "wb"
            ) as f:
                f.write(base64.b64decode(output))
            self.output = file_name  # file can then be found using the api
        elif self.type == "info" and success:
            self.device.address = output["address"]
            self.device.hostname = output["hostname"]
            self.device.username = output["username"]
            self.device.admin = output["admin"]
        else:
            self.output = output
        self.success = success
        self.finished_at = datetime.now()
        if success:
            LogEntryModel.log(
                "success",
                "devices",
                f"Task '{self.name}' finished successfully",
            )
        else:
            LogEntryModel.log(
                "danger",
                "devices",
                f"Task '{self.name}' finished with an error",
            )
        Session.commit()

    @staticmethod
    def generate_task(device_or_id: DeviceModel | int | str) -> "TaskModel":
        task = TaskModel()
        if type(device_or_id) == DeviceModel:
            task.device = device_or_id
        else:
            task.device_id = int(device_or_id)
        task.args = {}
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
        file.save(
            get_resource(
                "data/uploads", secure_filename(file.name), skip_file_check=True
            )
        )
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

    @staticmethod
    def get_info(device_or_id: DeviceModel | int) -> "TaskModel":
        """Create a Get-Info task.

        Args:
        -----
            device (DeviceModel): the device to execute the task
        """
        task = TaskModel.generate_task(device_or_id)
        task.type = "info"
        return task

    @staticmethod
    def execute_module(
        device_or_id: DeviceModel | int, path: str, execution_method: str, data: dict
    ) -> "TaskModel":
        """Create a Execute-Module task.

        Args:
        -----
            device_or_id (DeviceModel | int): the device to execute the task
            path (str): The path of the module
            execution_method (str): The execution method of the module
            data (dict): The data for the module
        """
        try:
            module = get_module(path)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(f"Module '{path}' not found.") from e

        if execution_method not in module.execution_methods:
            raise ValueError(
                f"Execution method '{execution_method}' not supported by module '{module.name}'."
            )

        # validate data
        data = module.options.validate_all(data)

        task = TaskModel.generate_task(device_or_id)
        task.type = "module"
        task.args["path"] = path
        task.args["execution_method"] = execution_method
        task.args.update(data)
        return task

    def get_module_code(self) -> str:
        """Get the code of the module.

        Returns:
        --------
            str: The code of the module
        """
        if self.type != "module":
            raise ValueError("Task is not a module task.")
        module = get_module(self.args["path"])
        return module.code(self.device, self.device.stager.listener, self.args)
