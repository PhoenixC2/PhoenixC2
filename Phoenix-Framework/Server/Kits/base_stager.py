from abc import abstractmethod
from typing import TYPE_CHECKING

from Utils.options import DefaultStagerPool, OptionPool

if TYPE_CHECKING:
    from Commander import Commander
    from Database import StagerModel


class BasePayload:
    supported_target_os: list[str] = []
    supported_target_arch: list[str] = []
    supported_server_os: list[str] = []
    compiled: bool = False
    options: OptionPool =  OptionPool()


    @abstractmethod
    def generate_payload(self, stager_db: "StagerModel") -> tuple[bytes | str, bool]:
        """ Generate the payload """
    
    @classmethod
    def to_dict(cls, commander : "Commander") -> dict:
        return {
            "supported_target_os": cls.supported_target_os,
            "supported_target_arch": cls.supported_target_arch,
            "supported_server_os": cls.supported_server_os,
            "compiled": cls.compiled,
            "options": cls.options.to_dict(commander)
        }


class BaseStager:
    name : str = "Base Stager"
    description : str = "This is the base stager"
    options = DefaultStagerPool()
    # The payloads that are supported by this stager and if they have to be compiled
    payloads: dict[str, BasePayload] = {}

    @abstractmethod
    def generate_stager(stager_db: "StagerModel") -> bytes | str:
        """Generate a stager based on the stager_db entry.

        Args:
            stager_db (StagerModel): The stager database entry.

        Returns:
            bytes | str: The stager or the stager path.
            bool: If the stager is a path or not.
            """
        # Credit to BC-Security/Empire for using jinja2 for stagers.
        pass
    
    @classmethod
    def to_dict(cls, commander: "Commander") -> dict:
        """Return a dict of the stager."""
        return {
            "name": cls.name,
            "description": cls.description,
            "options": cls.options.to_dict(commander),
            "payloads": {x: cls.payloads[x].to_dict(commander) for x in cls.payloads},
        }