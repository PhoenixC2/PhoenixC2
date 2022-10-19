from Utils.options import OptionPool
"""The base module class"""
class BaseModule:
    """This is the Base Class for all Modules."""
    name: str = "BaseModule"
    description: str = "This is the Base Class for all Modules."
    author: str = "Unknown"
    # The supported target OS for the module
    os: list[str] = ["linux", "windows", "osx"]
    options = OptionPool()
    # The unsupported stagers for the module
    stagers: list[str] = []
    # execution type
    # code - execute the code directly
    # shellcode - execute the code as shellcode
    # file - execute the code from a file
    execution_type: str = "code"
    