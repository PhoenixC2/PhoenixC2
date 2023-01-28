from phoenixc2.server.plugins.base import InjectedPlugin


class Plugin(InjectedPlugin):
    name = "test"

    def execute(self, commander: "Commander", config: dict) -> str:
        return "<script>alert('test')</script>"