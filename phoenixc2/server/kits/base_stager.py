import json
from abc import ABC
from typing import TYPE_CHECKING

from phoenixc2.server.utils.options import DefaultStagerPool
from .base_payload import BasePayload, FinalPayload

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander
    from phoenixc2.server.database import StagerModel


class BaseStager(ABC):
    name: str = "Base Stager"
    description: str = "This is the base stager"
    author: str = "Unknown"
    option_pool = DefaultStagerPool()
    payloads: dict[str, BasePayload] = {}

    @classmethod
    def generate(
        cls, stager_db: "StagerModel", recompile: bool = False
    ) -> FinalPayload:
        """Generate a stager based on the stager_db entry.

        Args:
        -----
            stager_db (StagerModel): The stager database entry.
            recompile (bool, optional): If the stager should be recompiled
        Returns:
        ------
            bytes | str: The stager or the stager path.
            bool: If the stager is a path or not.
        """
        # credit to BC-SECURITY/Empire for the using jinja2 for stagers
        if stager_db.payload not in cls.payloads:
            raise ValueError("Invalid payload type")

        return cls.payloads[stager_db.payload].generate(stager_db, recompile)

    @classmethod
    def to_dict(cls, commander: "Commander") -> dict:
        """Return a dict of the stager."""
        return {
            "name": cls.name,
            "description": cls.description,
            "options": cls.option_pool.to_dict(commander),
            "payloads": {x: cls.payloads[x].to_dict(commander) for x in cls.payloads},
        }

    @classmethod
    def to_json(cls, commander: "Commander") -> str:
        """Return a json of the stager."""
        return json.dumps(cls.to_dict(commander), default=str)

    @classmethod
    def __repr__(cls) -> str:
        return f"<Stager(name={cls.name}>"
