from phoenixc2.server.modules.base import BaseModule
from phoenixc2.server.utils.options import IntegerType, Option, OptionPool


class Module(BaseModule):
    name = "Get_Users"
    description = "Get all users on the system."

    def code(cls, device, listener, args):
        return f""