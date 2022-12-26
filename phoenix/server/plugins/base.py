from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from phoenix_framework.server.utils.options import OptionPool

if TYPE_CHECKING:
    from phoenix_framework.server.commander import Commander


class BasePlugin(ABC):
    """The Base Plugin class."""

    name: str
    description: str
    author: str
    os = ["linux", "windows", "osx"]
    options = OptionPool()
    # execution types:
    # - function - execute the function directly
    # - thread - execute the function in a thread
    # - process - execute the function in a process
    # - file - execute the function as an external file in a external process
    execution_type: str = "function"

    @abstractmethod
    def execute(self, commander: "Commander", config: dict) -> None:
        """The main function of the plugin to be executed

        Execution type:
        - file - return the path to the file to be executed in a external process
        - everything else - write the code to be executed in the function
        """
        pass

    @classmethod
    def to_dict(cls, commander: "Commander") -> dict:
        return {
            "name": cls.name,
            "description": cls.description,
            "author": cls.author,
            "os": cls.os,
            "options": cls.options.to_dict(commander),
            "execution_type": cls.execution_type,
        }
