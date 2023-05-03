import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from phoenixc2.server.kits.payload_base import FinalPayload
    from phoenixc2.server.commander.commander import Commander

from phoenixc2.server.utils.options import OptionPool


class BaseBypass(abc.ABC):
    """Base bypass class. All bypasses must inherit from this class.

    Attributes:
        name (str): Name of the bypass
        description (str): Description of the bypass
        author (str): Author of the bypass
        os (tuple): Tuple of supported operating systems
        options (OptionPool): OptionPool object containing the bypass options
        final (bool): If the bypass is final, it cannot be chained with other bypasses
        supported_languages (tuple): Tuple of supported languages
    """

    name: str
    description: str = ""
    author: str = ""
    os = ("windows", "linux", "macos")
    option_pool = OptionPool()
    final = False
    supported_languages = ()

    def execute(self, final_payload: "FinalPayload", args: dict = {}) -> "FinalPayload":
        """Executes the bypass

        Args:
            final_payload (FinalPayload): FinalPayload object
            args (dict, optional): Arguments to pass to the bypass

        Returns:
            FinalPayload: Modified FinalPayload object
        """
        if final_payload.payload.language not in self.supported_languages:
            raise Exception(
                f"Language of the payload is not supported by '{self.name}'."
            )

        self.generate(final_payload, args)

    @abc.abstractmethod
    def generate_body(
        self, final_payload: "FinalPayload", args: dict = {}
    ) -> str | bytes:
        """Generates the bypass body

        Args:
            final_payload (FinalPayload): FinalPayload object
            args (dict, optional): Arguments to pass to the bypass

        Returns:
            str | bytes: Bypass body
        """
        pass

    @abc.abstractmethod
    def generate(
        self, final_payload: "FinalPayload", args: dict = {}
    ) -> "FinalPayload":
        pass

    def to_dict(self, commander: "Commander") -> dict:
        """Returns the bypass as a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "os": self.os,
            "options": self.option_pool.to_dict(commander),
            "final": self.final,
        }

    def __repr__(self) -> str:
        return f"<Bypass(name={self.name})>"
