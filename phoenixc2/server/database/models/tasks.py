"""The Tasks Model"""
import base64
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.utils import secure_filename

from phoenixc2.server.database.base import Base
from phoenixc2.server.database.engine import Session
from phoenixc2.server.modules import get_module
from phoenixc2.server.utils.misc import Status, generate_name
from phoenixc2.server.utils.resources import get_resource

from .credentials import CredentialModel
from .devices import DeviceModel
from .logs import LogEntryModel

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander
    from phoenixc2.server.modules.base import BaseModule


class TaskModel(Base):
    """The Tasks Model."""

    __tablename__ = "Tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(10), unique=True, default=generate_name)
    description: Mapped[Optional[str]] = mapped_column(Text)
    action: Mapped[str] = mapped_column(String(10))
    args: Mapped[Optional[dict]] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict
    )
    success: Mapped[Optional[bool]] = mapped_column(Boolean)
    output: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=datetime.now
    )
    device_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("Devices.id"))
    device: Mapped["DeviceModel"] = relationship("DeviceModel", back_populates="tasks")

    @property
    def finished(self) -> bool:
        return self.finished_at is not None

    @property
    def operation(self) -> str:
        return self.device.operation

    def to_dict(self, commander: "Commander", show_device: bool = False) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "action": self.action,
            "args": self.args,
            Status.Success: self.success,
            "created_at": self.created_at,
            "finished_at": self.finished_at,
            "output": self.output,
            "device": self.device.to_dict(commander)
            if show_device and self.device is not None
            else self.device_id,
        }

    def get_module(self) -> "BaseModule":
        """Get the module class for this task."""
        if self.action != "module":
            raise ValueError("Task is not a module task.")
        module = get_module(self.args["path"])
        return module

    def finish(self, output: str | dict, success: bool, credentials: dict = [None]):
        """Update the Task status and output.
        Still has to be committed!"""

        if self.action == "download" and success:
            file_name = secure_filename(self.args["target_path"].split("/")[-1])
            # save file to downloads folder
            with get_resource("data/downloads/", file_name, skip_file_check=True).open(
                "wb"
            ) as f:
                f.write(base64.b64decode(output))
            self.output = file_name  # file can then be found using the api

        elif self.action == "info" and success:
            self.device.address = output.get("address", self.device.address)
            self.device.hostname = output.get("hostname", self.device.hostname)
            self.device.user = output.get("username", self.device.user)
            self.device.admin = output.get("admin", self.device.admin)
        elif self.action == "module" and success:
            module = self.get_module()
            self.output = module.finish(self, output)
        else:
            self.output = output

        self.success = success
        self.finished_at = datetime.now()

        # save credentials

        for credential in credentials:
            try:
                created_cred = CredentialModel.create(
                    credential["value"],
                    credential["hash"],
                    credential["user"],
                    credential["admin"],
                )
                created_cred.operation = self.operation
            except Exception as e:
                LogEntryModel.log(
                    Status.Danger,
                    "credentials",
                    f"Failed to add new credential to the database: {e}",
                )
                continue

            Session.add(created_cred)
            LogEntryModel.log(
                Status.Success,
                "credentials",
                "New credential added to the database",
            )

        if success:
            LogEntryModel.log(
                Status.Success,
                "devices",
                f"Task '{self.name}' finished successfully",
            )
        else:
            LogEntryModel.log(
                Status.Danger,
                "devices",
                f"Task '{self.name}' finished with an error",
            )

    def delete(self):
        """Delete the task."""
        if self.action == "upload":
            # delete uploaded file
            try:
                get_resource("data/uploads/", self.name).unlink()
            except FileNotFoundError:
                pass
        Session.delete(self)

    @staticmethod
    def generate_task(device_or_id: DeviceModel | int | str) -> "TaskModel":
        """Generate a new task for the given device."""
        task = TaskModel()
        task.name = generate_name()
        if isinstance(device_or_id, DeviceModel):
            task.device = device_or_id
        else:
            device = Session.query(DeviceModel).filter_by(id=device_or_id).first()
            if device is None:
                raise ValueError("Device not found.")
            task.device = device
        task.args = {}
        return task

    """ default methods for every stager """

    @staticmethod
    def upload(
        device_or_id: DeviceModel | int, file_content: bytes, target_path: str
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

        task = TaskModel.generate_task(device_or_id)

        with get_resource("data/uploads/", task.name, skip_file_check=True).open(
            "wb"
        ) as f:
            f.write(file_content)

        task.action = "upload"
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
        task.action = "download"
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
        task.action = "reverse-shell"
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
        task.action = "rce"
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
        task.action = "dir"
        task.args["dir"] = dir
        return task

    @staticmethod
    def get_infos(device_or_id: DeviceModel | int) -> "TaskModel":
        """Create a Get-Info task.

        Args:
        -----
            device (DeviceModel): the device to execute the task
        """
        task = TaskModel.generate_task(device_or_id)
        task.action = "info"
        return task

    @staticmethod
    def execute_module(
        device_or_id: DeviceModel | int | str,
        path: str,
        execution_method: str,
        data: dict,
    ) -> "TaskModel":
        """Create a Execute-Module task.

        Args:
        -----
            device_or_id (DeviceModel | int): the device to execute the task
            path (str): The path of the module
            execution_method (str): The execution method of the module
            data (dict): The data for the module
        """

        module = get_module(path)

        if execution_method not in module.execution_methods:
            raise ValueError(
                f"Execution method not supported by module '{module.name}'."
            )

        # validate data
        data = module.option_pool.validate_all(data)

        task = TaskModel.generate_task(device_or_id)
        task.action = "module"
        task.args["path"] = path
        task.args["execution_method"] = execution_method
        task.args.update(data)
        return task

    def __repr__(self) -> str:
        return f"<TaskModel(id={self.id}, action={self.action}, device={self.device})>"
