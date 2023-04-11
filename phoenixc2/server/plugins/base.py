import subprocess
import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import importlib
from flask import Blueprint

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander
    from phoenixc2.server.database import DeviceModel


class BasePlugin(ABC):
    """The Base Plugin class."""

    name: str
    description: str
    author: str
    os: list[str] = ["linux", "windows", "osx"]
    required_dependencies: list[tuple[str, str]] = []  # (package, version)

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
                    try:
                        importlib.import_module(package)
                    except ImportError:
                        return False
                else:
                    try:
                        importlib.import_module(package)
                    except ImportError:
                        return False
                    if importlib.metadata.version(package) != version:
                        return False
            except subprocess.CalledProcessError:
                return False
        return True

    @staticmethod
    @abstractmethod
    def execute(commander: "Commander", config: dict) -> any:
        """Base execute function for most plugin types."""
        pass


class BlueprintPlugin(BasePlugin):
    """The Base Web Plugin class.

    Used for plugins which modify the api.
    """

    @staticmethod
    @abstractmethod
    def execute(commander: "Commander", config: dict) -> Blueprint:
        """Returns the blueprint to be added to the web api."""
        pass


class RoutePlugin(BasePlugin):
    """The Base Route Plugin class.

    Used for plugins which add own routes to the web api.
    """

    commander: "Commander" = None
    # has to be set because you can't pass the commander to the execute function
    rule: str  # the rule to be added to the web api

    @staticmethod
    @abstractmethod
    def execute():
        """The function to be added to the route."""
        pass


class ExecutedPlugin(BasePlugin):
    """The Base Executed Plugin class.

    Used for plugins that are executed on the server, like a service or a script.
    """

    # execution types:
    # - direct - execute the code directly
    # - thread - execute the function in a thread
    # - process - execute the function in a process
    execution_type: str = "direct"

    @staticmethod
    @abstractmethod
    def execute(commander, config) -> str | None:
        """The main code of the plugin to be executed

        Execution type:
        - file - return the path to the file to be executed in a external process
        - everything else - write the code to be executed in the function
        """
        pass


class PolyPlugin(BasePlugin):
    """The Base Poly Plugin class.

    Used for multiple plugin types in one package.
    """

    plugins: list[BasePlugin] = []


class ConnectionEventPlugin(BasePlugin):
    """The Base Connection Event Plugin class.

    Used for plugins that are executed when a connection is established.
    """

    @staticmethod
    @abstractmethod
    def execute(device: "DeviceModel", config: dict) -> None:
        """Executed when a connection is established."""
        pass
