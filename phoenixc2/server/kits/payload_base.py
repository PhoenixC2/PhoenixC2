from typing import TYPE_CHECKING, BinaryIO
from abc import ABC, abstractmethod
from tempfile import TemporaryFile
from pathlib import Path
from phoenixc2.server.utils.options import OptionPool
from phoenixc2.server.utils.features import Feature
from phoenixc2.server.utils.resources import get_resource

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander
    from phoenixc2.server.database import StagerModel


class BasePayload(ABC):
    name = "BasePayload"
    description = "BasePayload"
    author: str = "Screamz2k"
    supported_target_os: list[str] = ["linux", "windows", "osx"]
    supported_target_arch: list[str] = ["*"]
    module_execution_methods: list[str] = [
        "command",
        "direct",
        "thread",
        "process",
        "injection",
        "external",
    ]
    module_code_types: list[str] = ["shellcode", "compiled", "native"]
    module_languages: list[str] = ["python"]
    language = "python"
    end_format: str = ""
    compiled: bool = False
    option_pool: OptionPool = OptionPool()
    features: list[Feature] = []

    @classmethod
    def get_output_file(cls, stager_db: "StagerModel") -> Path:
        """Save the output to the stager file"""
        return get_resource(
            "data/stagers", f"{stager_db.id}{cls.end_format}", skip_file_check=True
        )

    @classmethod
    @abstractmethod
    def generate(
        cls, stager_db: "StagerModel", recompile: bool = False
    ) -> "FinalPayload":
        """Generate the payload"""
        ...

    @classmethod
    @abstractmethod
    def already_compiled(cls, stager_db: "StagerModel") -> bool:
        """Return if the payload was already compiled"""
        if cls.compiled:
            return cls.get_output_file(stager_db).exists()
        return False

    @classmethod
    def to_dict(cls, commander: "Commander") -> dict:
        return {
            "name": cls.name,
            "description": cls.description,
            "author": cls.author,
            "supported_target_os": cls.supported_target_os,
            "supported_target_arch": cls.supported_target_arch,
            "supported_execution_methods": cls.module_execution_methods,
            "supported_code_types": cls.module_code_types,
            "supported_languages": cls.module_languages,
            "language": cls.language,
            "end_format": cls.end_format,
            "compiled": cls.compiled,
            "options": cls.option_pool.to_dict(commander),
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} language={self.language}>"


class FinalPayload:
    payload: BasePayload
    stager: "StagerModel"
    output: bytes | str

    def __init__(self, payload: BasePayload, stager_db: "StagerModel"):
        self.stager: "StagerModel" = stager_db
        self.payload: BasePayload = payload

    @property
    def name(self) -> str:
        return self.stager.name + "." + self.payload.end_format

    @property
    def as_file(self) -> BinaryIO:
        # check if the output is string or bytes and create temporary file
        file = TemporaryFile()
        if isinstance(self.output, str):
            file.write(self.output.encode())
        else:
            file.write(self.output)
        file.seek(0)
        return file

    def set_output_from_path(self, path: str | Path) -> None:
        """Set the output from a file path"""
        with open(str(path), "rb") as file:
            self.output = file.read()

    def set_output_from_file(self, file: BinaryIO) -> None:
        """Set the output from a file object"""
        self.output = file.read()

    def set_output_from_content(self, content: bytes | str) -> None:
        """Set the output from a string or bytes"""
        self.output = content

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} output={len(self.output)}>"
