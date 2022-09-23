import importlib
import io
from abc import abstractmethod

from cryptography.fernet import Fernet
from Database import DeviceModel, TasksModel, db_session
from Modules.base import BaseModule


class BaseHandler():
    """The Base Handler Class for all Devices"""

    def __str__(self) -> TasksModel:
        return str(self.addr)

    def __init__(self, addr: str, id: int):
        self.addr = addr
        self.id = id
        self.device_db: DeviceModel
        self.tasks: list[TasksModel] = []
        self.modules: list[BaseModule] = []

    def decrypt(self, data: str):
        """Decrypt the data"""
        return self.fernet.decrypt(data).decode()

    def encrypt(self, data: str):
        """Encrypt the data"""
        return self.fernet.encrypt(data.encode())

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


