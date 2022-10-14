from typing import TYPE_CHECKING
from abc import abstractmethod
if TYPE_CHECKING:
    from Utils.options import OptionPool
    from Database import StagerModel


class BaseStager:
    option_pool: "OptionPool"

    @abstractmethod
    def generate_stager(stager_db : "StagerModel") -> bytes | str:
        """Generate a stager based on the stager_db entry.
        
        Args:
            stager_db (StagerModel): The stager database entry.
        
        Returns:
            bytes | str: The stager or the stager path.
            bool: If the stager is a path or not.
            """
        pass