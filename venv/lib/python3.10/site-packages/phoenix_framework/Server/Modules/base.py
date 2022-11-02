from Database import DeviceModel
from Utils.options import OptionPool

"""The base module class"""
class BaseModule:
    """This is the Base Class for all Modules."""
    name: str = "BaseModule"
    description: str = "This is the Base Class for all Modules."
    author: str = "Screamz2k"
    language: str = "python"
    os: list[str] = ["linux", "windows", "osx"]
    options = OptionPool()
    stagers: list[str] = []
    admin : bool = False
    # execution types:
    # - code - execute the code directly
    # - shellcode - execute the code as shellcode
    # - file - execute the code as an external file
    execution_type: str = "code"

    
    def __init__(self, device: DeviceModel):
        self.device = device
    
    @property
    def code(self) -> str:
        """The code to be executed"""
        # Code can be modified here
        return ""