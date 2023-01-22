import subprocess
import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from phoenixc2.server.utils.options import OptionPool

if TYPE_CHECKING:
    from phoenixc2.server.commander import Commander


class BasePlugin(ABC):
    """The Base Plugin class."""

    name: str
    description: str
    author: str
    os: list[str] = ["linux", "windows", "osx"]
    required_dependencies: list[tuple[str, str]] = []  # (package, version)
    # execution types:
    # - direct - execute the code directly
    # - thread - execute the function in a thread
    # - process - execute the function in a process
    # - file - execute the function as an external file in an external process
    execution_type: str = "direct"

    @abstractmethod
    def execute(self, commander: "Commander", config: dict) -> str | None:
        """The main code of the plugin to be executed

        Execution type:
        - file - return the path to the file to be executed in a external process
        - everything else - write the code to be executed in the function
        """
        pass

    @classmethod
    def to_dict(cls) -> dict:
        return {
            "name": cls.name,
            "description": cls.description,
            "author": cls.author,
            "os": cls.os,
            "required_dependencies": cls.required_dependencies,
            "execution_type": cls.execution_type,
        }

    @classmethod
    def install_dependencies(cls) -> None:
        """Install the required dependencies for the plugin."""
        for package, version in cls.required_dependencies:
            if not version or version == "latest":
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", f"{package}"]
                )
            else:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", f"{package}=={version}"]
                )

    @classmethod
    def check_dependencies(cls) -> bool:
        """Check if the required dependencies for the plugin are installed."""
        for package, version in cls.required_dependencies:
            try:
                if not version or version == "latest":
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "show", f"{package}"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "show", f"{package}=={version}"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
            except subprocess.CalledProcessError:
                return False
        return True
