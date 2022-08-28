from Utils.libraries import importlib, Fernet
from Modules.base import Base_Module
from abc import ABC, abstractmethod


class Base_Handler(metaclass=ABC):
    """The Base Handler Class for all Devices"""

    def __str__(self) -> str:
        return str(self.addr)

    def __init__(self, addr: str, key: bytes, id: int):
        self.addr = addr
        self.fernet = Fernet(key)
        self.id = id
        self.modules: list[Base_Module] = []

    def decrypt(self, data: str):
        """Decrypt the data"""
        return self.fernet.decrypt(data).decode()

    def encrypt(self, data: str):
        """Encrypt the data"""
        return self.fernet.encrypt(data.encode())

    def load_module(self, name: str, load_module: bool = True):
        """Load a module"""
        # Get module
        module: Base_Module = importlib.import_module(
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
    def execute_module(self, name: str):
        ...

    @abstractmethod
    def alive(self):
        """Checks if device is alive

        Returns:
            bool: True if yes, False if not
        """
    @abstractmethod
    def reverse_shell(self, address: str, port: int):
        """Open a Reverse Shell to a given Address:Port
        Args:
            address (str): Receiver Address
            port (int): Receiver Port

        Returns:
            str: Output or Error Message
        """
    @abstractmethod
    def file_upload(self, local_file: str, remote_path: str):
        """Upload a File to a Device
        Args:
            local_file (string): Local file to upload
            remote_path (string): Remote path to upload the file to
        Returns:
            str: Output or Error Message
        """
        ...

    @abstractmethod
    def file_download(self, local_path: str, remote_file: str):
        """Download a file from the device
        Args:
            local_path (string): Local path to save the file to
            remote_file (string): Remote File to download the file from
        Returns:
            str: Output or Error Message
        """
        ...

    @abstractmethod
    def rce(self, cmd: str):
        """Send a Cmd to a Device and return the Output
        Args:
            cmd (str): Command to execute
        Returns:
            str: Output of the command or Error Message
        """
        ...

    @abstractmethod
    def get_directory_contents(self, dir:str):
        """Get the contents of a directory
        Args:
            dir (str): Directory to get the contents of
        Returns:
            output (str): Output or Error Message
        """
        ...
    @abstractmethod
    def get_file_contents(self, path:str):
        """Get the contents of a file
        Args:
            path (str): Path to the file
        Returns:
            output (str): Output or Error Message
        """
        ...