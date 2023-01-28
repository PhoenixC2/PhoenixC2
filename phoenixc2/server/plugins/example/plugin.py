import time

from phoenixc2.server.plugins.base import ExecutedPlugin


class Plugin(ExecutedPlugin):
    """Example Plugin"""

    name = "example"
    description = "Example Plugin"
    author = "Screamz2k"
    os = ["linux", "windows", "osx"]
    execution_type = "thread"

    def execute(self, commander, config) -> None:
        # import your dependencies here to avoid import errors
        while True:
            time.sleep(config["interval"])
            print("Hello World!")
