from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from phoenixc2.server.utils.options import OptionPool

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander
    from phoenixc2.server.database import TaskModel


class BaseModule(ABC):
    """This is the Base Class for all Modules."""

    name: str = "BaseModule"
    description: str = "This is the Base Class for all Modules."
    author: str = "Screamz2k"
    language: str = "python"
    os: list[str] = ["linux", "windows", "osx"]
    option_pool = OptionPool()
    admin_required: bool = False
    # code types:
    # - native: code is written in the language of the module
    # - shellcode: shellcode
    # - compiled: a compiled binary
    code_type: str = "native"
    # execution methods:
    # - command: execute a command
    # - direct: normal code & shellcode
    # - thread: normal code
    # - process: normal code
    # - injection: inject shellcode into a process
    # - external: create a file save the binary content to it and execute it externally
    execution_methods: list[str] = [
        "command",
        "direct",
        "thread",
        "process",
        "injection",
        "external",
    ]

    @staticmethod
    @abstractmethod
    def code(task: "TaskModel") -> str | bytes:
        """The code to be executed"""
        pass

    @classmethod
    def to_dict(cls, commander: "Commander") -> dict:
        return {
            "name": cls.name,
            "description": cls.description,
            "author": cls.author,
            "language": cls.language,
            "os": cls.os,
            "options": cls.option_pool.to_dict(commander),
            "admin": cls.admin_required,
            "code_type": cls.code_type,
            "execution_methods": cls.execution_methods,
        }

    @classmethod
    def finish(cls, task: "TaskModel", data: str | bytes) -> str | bytes:
        """This function is used to process the output of the module"""
        return data
