from phoenixc2.server.plugins.base import RoutePlugin


class Plugin(RoutePlugin):
    name = "Test"
    rule = "/test"

    def execute(self):
        return "test"
