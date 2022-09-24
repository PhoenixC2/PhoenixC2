import importlib
import io
from datetime import datetime
from abc import abstractmethod

from Utils.ui import log
from Database import DeviceModel, TasksModel, db_session
from Modules.base import BaseModule


class BaseHandler():
    """The Base Handler Class for all Devices"""

    def __str__(self) -> TasksModel:
        return str(self.addr)

    def __init__(self, addr: str, db_entry: DeviceModel):
        self.db_entry = db_entry
        self.addr = addr
        self.id = db_entry.id
        self.name = db_entry.name
        self.modules: list[BaseModule] = []

    '''    def decrypt(self, data: str):
            """Decrypt the data"""
            return self.fernet.decrypt(data).decode()

        def encrypt(self, data: str):
            """Encrypt the data"""
            return self.fernet.encrypt(data.encode())'''

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

    def add_task(self, task: TasksModel):
        self.tasks.append(task)
    
    def finish_task(self, task: TasksModel, output: str):
        task.output = output
        task.finished_at = datetime.now()
        db_session.commit()
        log(f"Finished Task '{task.name}' of type '{task.type}'", "success")
        
    
    def get_task(self, id_or_name: int|str) -> TasksModel:
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
    
    @abstractmethod
    def execute_module(self, name: str) -> TasksModel:
        ...

    @abstractmethod
    def alive(self) -> bool:
        """Checks if device is alive

        Returns:
            bool: True if yes, False if not
        """
    @abstractmethod
    def reverse_shell(self, address: str, port: int) -> TasksModel:
        """Open a Reverse Shell to a given Address:Port
        Args:
            address (str): Receiver Address
            port (int): Receiver Port

        """
    @abstractmethod
    def file_upload(self, local_file: io.TextIOWrapper, remote_path: str) -> TasksModel:
        """Upload a File to a Device
        Args:
            local_file (string): Local file to upload
            remote_path (string): Remote path to upload the file to
        """
        ...

    @abstractmethod
    def file_download(self, remote_path: str) -> TasksModel:
        """Download a file from the device
        Args:
            remote_path (string): Remote File to download the file from
        """
        ...

    @abstractmethod
    def rce(self, cmd: str) -> TasksModel:
        """Send a Cmd to a Device and return the Output
        Args:
            cmd (str): Command to execute
        """
        ...

    @abstractmethod
    def get_directory_contents(self, dir: str) -> TasksModel:
        """Get the contents of a directory
        Args:
            dir (str): Directory to get the contents of
        """
        ...


