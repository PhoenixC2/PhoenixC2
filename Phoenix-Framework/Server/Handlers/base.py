import importlib
import io
from abc import abstractmethod
from datetime import datetime
from uuid import uuid1

from Database import DeviceModel, Session, TaskModel
from Modules.base import BaseModule
from Utils.ui import log


class BaseHandler():
    """The Base Handler Class for all Devices"""

    def __str__(self) -> TaskModel:
        return str(self.addr)

    def __init__(self, db_entry: DeviceModel):
        self.addr = db_entry.address
        self.id = db_entry.id
        self.name = db_entry.name
        self.modules: list[BaseModule] = []

    '''    def decrypt(self, data: str):
            """Decrypt the data"""
            return self.fernet.decrypt(data).decode()

        def encrypt(self, data: str):
            """Encrypt the data"""
         return self.fernet.encrypt(data.encode())'''
    @property
    def db_entry(self):
        return Session().query(DeviceModel).filter_by(id=self.id).first()
    def load_module(self, name: str, load_module: bool = True) -> BaseModule:
        """Load a module"""
        # Get module
        module: BaseModule = importlib.import_module(
            "Modules." + name).Module()
        if load_module:
            module.load()
        # Add to list
        self.modules.append(module)
        # Return module

        return module

    def unload_module(self, name: str):
        """Unload a module"""
        # Get module
        for module in self.modules:
            if module.name == name:
                self.modules.remove(module)
                return module
        raise Exception("Module not found")

    def generate_task(self) -> TaskModel:
        return TaskModel(
            name=str(uuid1()),
            device=self.db_entry,
            created_at=datetime.now()
        )
    def add_task(self, task: TaskModel):
        self.tasks.append(task)

    def finish_task(self, task: TaskModel, output: str):
        task.output = output
        task.finished_at = datetime.now()
        Session.commit()
        log(f"Finished Task '{task.name}' of type '{task.type}'", "success")

    def get_task(self, id_or_name: int | str) -> TaskModel:
        """Return a task based on its id or name."""
        if type(id_or_name) == int:
            for task in self.db_entry.tasks:
                if task.id == id_or_name:
                    return task
        else:
            for task in self.db_entry.tasks:
                if task.name == id_or_name:
                    return task

    @abstractmethod
    def execute_module(self, name: str) -> TaskModel:
        ...

    @abstractmethod
    def alive(self) -> bool:
        """Checks if device is alive

        Returns:
            bool: True if yes, False if not
        """
    @abstractmethod
    def reverse_shell(self, address: str, port: int, binary: str) -> TaskModel:
        """Open a Reverse Shell to a given Address:Port
        Args:
            address (str): Receiver Address
            port (int): Receiver Port
            binary (str): Executed binary

        """
    @abstractmethod
    def file_upload(self, local_file: io.TextIOWrapper, remote_path: str) -> TaskModel:
        """Upload a File to a Device
        Args:
            local_file (string): Local file to upload
            remote_path (string): Remote path to upload the file to
        """
        ...

    @abstractmethod
    def file_download(self, remote_path: str) -> TaskModel:
        """Download a file from the device
        Args:
            remote_path (string): Remote File to download the file from
        """
        ...

    @abstractmethod
    def rce(self, cmd: str) -> TaskModel:
        """Send a Cmd to a Device and return the Output
        Args:
            cmd (str): Command to execute
        """
        ...

    @abstractmethod
    def get_directory_contents(self, dir: str) -> TaskModel:
        """Get the contents of a directory
        Args:
            dir (str): Directory to get the contents of
        """
        ...
