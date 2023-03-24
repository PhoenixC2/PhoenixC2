import abc
from phoenixc2.server.database import StagerModel
from phoenixc2.server.utils.options import OptionPool


class BaseBypass(abc.ABC):
    """Base bypass class. All bypasses must inherit from this class.

    Attributes:
        name (str): Name of the bypass
        description (str): Description of the bypass
        os (tuple): Tuple of supported operating systems
        options (OptionPool): OptionPool object containing the bypass options
        final (bool): If the bypass is final, it cannot be chained with other bypasses
    """

    name: str
    description: str
    os = ("windows", "linux", "macos")
    option_pool = OptionPool()
    final = False

    @abc.abstractmethod
    def generate(self, stager: StagerModel, args: dict = {}) -> str | bytes:
        pass
