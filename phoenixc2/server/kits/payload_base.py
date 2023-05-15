import shutil
import uuid
from typing import TYPE_CHECKING, BinaryIO
from abc import ABC, abstractmethod
from tempfile import TemporaryFile
from pathlib import Path
from phoenixc2.server.utils.options import OptionPool
from phoenixc2.server.utils.features import Feature
from phoenixc2.server.utils.resources import get_resource

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander
    from phoenixc2.server.database import StagerModel, DeviceIdentifierModel


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
    file_ending: str = ""
    compiled: bool = False
    option_pool: OptionPool = OptionPool()
    features: list[Feature] = []
    # applications which have to be installed on the system
    required_applications: list[str] = []

    @classmethod
    def check_for_required_applications(cls):
        """Check if all required applications are installed

        Raises:
        ------
            `FileNotFoundError`:
                If an application is not installed.
        """

        for application in cls.required_applications:
            if shutil.which(application) is None:
                raise FileNotFoundError(
                    f"Application {application} " "is required to compile this payload"
                )

    @classmethod
    def generate_uid(cls) -> str:
        """Generate a unique identifier for the payload

        Returns:
        ------
            `str`:
                The unique identifier.
        """
        return str(uuid.uuid4())

    @classmethod
    def get_output_file(cls, stager_db: "StagerModel") -> Path:
        """Get the output file for the payload

        Args:
        -----
            stager_db: `StagerModel`
                The stager database entry.

        Returns:
        ------
            `Path`:
                The output file.
        """
        return get_resource(
            "data/stagers", f"{stager_db.id}.stager", skip_file_check=True
        )

    @classmethod
    @abstractmethod
    def generate(
        cls,
        stager_db: "StagerModel",
        recompile: bool = False,
        identifier: "DeviceIdentifierModel" = None,
    ) -> "FinalPayload":
        """Generate the payload

        Args:
        -----
            stager_db: `StagerModel`
                The stager database entry.
            recompile: `bool`
                If the stager should be recompiled.
            identifier: `DeviceIdentifierModel`
                The device identifier database entry.

        Returns:
        ------
            `FinalPayload`:
                The final payload.
        """
        ...

    @classmethod
    @abstractmethod
    def already_compiled(cls, stager_db: "StagerModel") -> bool:
        """Return if the payload was already compiled

        Args:
        -----
            stager_db: `StagerModel`
                The stager database entry.

        Returns:
        ------
            `bool`:
                If the payload was already compiled.
        """

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
            "file_ending": cls.file_ending,
            "compiled": cls.compiled,
            "options": cls.option_pool.to_dict(commander),
            "features": [feature.to_dict() for feature in cls.features],
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} language={self.language}>"


class FinalPayload:
    payload: BasePayload
    stager: "StagerModel"
    output: bytes | str
    _file_ending: str = None

    def __init__(self, payload: BasePayload, stager_db: "StagerModel"):
        self.stager: "StagerModel" = stager_db
        self.payload: BasePayload = payload

    @property
    def file_ending(self) -> str:
        if self._file_ending is not None:
            return self._file_ending
        return self.payload.file_ending

    @file_ending.setter
    def file_ending(self, value: str) -> None:
        self._file_ending = value

    @property
    def name(self) -> str:
        return self.stager.name + self.file_ending

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
