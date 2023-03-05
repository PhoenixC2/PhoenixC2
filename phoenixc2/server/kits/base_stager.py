import json
from abc import abstractmethod
from typing import TYPE_CHECKING

from phoenixc2.server.utils.features import Feature
from phoenixc2.server.utils.options import DefaultStagerPool, OptionPool

if TYPE_CHECKING:
    from phoenixc2.server.commander import Commander
    from phoenixc2.server.database import StagerModel


class BasePayload:
    name = "BasePayload"
    description = "BasePayload"
    author: str = "Screamz2k"
    supported_target_os: list[str] = ["linux", "windows", "osx"]
    supported_target_arch: list[str] = ["x64", "x86"]
    module_execution_methods: list[str] = [
        "process",
        "injection",
    ]
    module_code_types: list[str] = ["shellcode", "compiled", "native"]
    module_languages: list[str] = ["python"]
    end_format: str = ""
    compiled: bool = False
    options: OptionPool = OptionPool()
    features: list[Feature] = []

    @abstractmethod
    def generate(
        self, stager_db: "StagerModel", one_liner: bool = False, recompile: bool = False
    ) -> "FinalPayload":
        """Generate the payload"""
        ...

    @classmethod
    def is_compiled(stager_db: "StagerModel") -> bool:
        """Return if the payload was already compiled"""
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
            "end_format": cls.end_format,
            "compiled": cls.compiled,
            "options": cls.options.to_dict(commander),
        }


class FinalPayload:
    def __init__(
        self, payload: BasePayload, stager_db: "StagerModel", output: bytes | str
    ):
        self.output: bytes | str = output
        self.stager: "StagerModel" = stager_db
        self.payload: BasePayload = payload

    @property
    def name(self) -> str:
        return self.stager.name + "." + self.payload.end_format


class BaseStager:
    name: str = "Base Stager"
    description: str = "This is the base stager"
    author: str = "Unknown"
    options = DefaultStagerPool()
    # The payloads that are supported by this stager and if they have to be compiled
    payloads: dict[str, BasePayload] = {}

    @classmethod
    def generate(
        cls, stager_db: "StagerModel", one_liner: bool = False, recompile: bool = False
    ) -> FinalPayload:
        """Generate a stager based on the stager_db entry.

        Args:
        -----
            stager_db (StagerModel): The stager database entry.
            one_liner (bool, optional): If the stager should be generated as a one-liner. Defaults to False.
            recompile (bool, optional): If the stager should be recompiled. Defaults to False.
        Returns:
        ------
            bytes | str: The stager or the stager path.
            bool: If the stager is a path or not.
        """
        # credit to BC-SECURITY/Empire for the using jinja2 for stagers
        if stager_db.payload not in cls.payloads:
            raise ValueError("Invalid payload type")

        return cls.payloads[stager_db.payload].generate(stager_db, one_liner, recompile)

    @classmethod
    def to_dict(cls, commander: "Commander") -> dict:
        """Return a dict of the stager."""
        return {
            "name": cls.name,
            "description": cls.description,
            "options": cls.options.to_dict(commander),
            "payloads": {x: cls.payloads[x].to_dict(commander) for x in cls.payloads},
        }

    @classmethod
    def to_json(cls, commander: "Commander") -> str:
        """Return a json of the stager."""
        return json.dumps(cls.to_dict(commander), default=str)
