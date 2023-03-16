import subprocess
import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from flask import Blueprint

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander


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


class BlueprintPlugin(BasePlugin):
    """The Base Web Plugin class.

    Used for plugins which modify the api.
    """

    @abstractmethod
    def execute(self, commander: "Commander", config: dict) -> Blueprint:
        """Returns the blueprint to be added to the web api."""
        pass


class RoutePlugin(BasePlugin):
    """The Base Template Plugin class.

    Used for plugins which add own routes to the web api.
    """

    commander: "Commander" = None
    # has to be set because you can't pass the commander to the execute function
    rule: str  # the rule to be added to the web api

    @abstractmethod
    def execute():
        """Returns the function to be added to the route."""
        pass


class InjectedPlugin(BasePlugin):
    """The Base Injected Plugin class.

    Used for plugins which inject code into existing templates, like html, js, css, etc.
    """

    # the name of the template to be modified
    # * - all templates
    # - list of templates
    templates: list[str] = ["*"]

    @abstractmethod
    def execute(self, commander: "Commander", config: dict) -> str:
        """Returns the code to be injected into the template."""
        pass


class ExecutedPlugin(BasePlugin):
    """The Base Executed Plugin class.

    Used for plugins that are executed on the server, like a service or a script.
    """

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
