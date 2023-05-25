from abc import ABC
from typing import TYPE_CHECKING

from phoenixc2.server.utils.options import DefaultStagerPool
from .payload_base import BasePayload, FinalPayload

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander
    from phoenixc2.server.database import StagerModel, DeviceIdentifierModel


class BaseStager(ABC):
    """The stager class is an abstract which handles the payloads and options."""

    name: str = "Base Stager"
    option_pool = DefaultStagerPool()
    payloads: dict[str, BasePayload] = {}

    @classmethod
    def generate(
        cls,
        stager_db: "StagerModel",
        recompile: bool = False,
        identifier: "DeviceIdentifierModel" = None,
    ) -> FinalPayload:
        """Generate a stager based on the stager_db entry.

        Args:
        -----
            stager_db: `StagerModel`
                The stager database entry.
            recompile: `bool`
                If the stager should be recompiled.
            identifier: `DeviceIdentifierModel`
                The device identifier to use for the stager.

        Returns:
        ------
            `FinalPayload`:
                The final payload.
        """
        # credit to BC-SECURITY/Empire for the using jinja2 for stagers
        if stager_db.payload not in cls.payloads:
            raise ValueError("Invalid payload type")

        return cls.payloads[stager_db.payload].generate(
            stager_db, recompile, identifier
        )

    @classmethod
    def to_dict(cls, commander: "Commander") -> dict:
        """Return a dict of the stager."""
        return {
            "name": cls.name,
            "options": cls.option_pool.to_dict(commander),
            "payloads": {x: cls.payloads[x].to_dict(commander) for x in cls.payloads},
        }

    @classmethod
    def __repr__(cls) -> str:
        return f"<Stager(name={cls.name}>"
