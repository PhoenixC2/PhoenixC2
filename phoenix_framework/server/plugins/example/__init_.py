from typing import TYPE_CHECKING
from phoenix_framework.server.plugins import BasePlugin
from phoenix_framework.server.utils.options import OptionPool

if TYPE_CHECKING:
    from phoenix_framework.server.commander.commander import Commander

class Plugin(BasePlugin):
    """Example Plugin"""
    name = "example"
    description = "Example Plugin"
    author = "Screamz2k"
    os = ["linux", "windows", "osx"]
    options = OptionPool()
    execution_type = "function"

    def execute(self, commander: "Commander") -> None:
        print("Hello World!")

        