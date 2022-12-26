import time

from phoenix_framework.server.plugins import BasePlugin
from phoenix_framework.server.utils.options import OptionPool


class Plugin(BasePlugin):
    """Example Plugin"""

    name = "example"
    description = "Example Plugin"
    author = "Screamz2k"
    os = ["linux", "windows", "osx"]
    options = OptionPool()
    execution_type = "thread"

    def execute(self, commander, config) -> None:
        while True:
            time.sleep(config["interval"])
            print("Hello World!")
