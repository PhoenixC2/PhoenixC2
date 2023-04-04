from phoenixc2.server.modules.base import BaseModule


class Module(BaseModule):
    name = "Get_Users"
    description = "Get a list of users and their privileges on the system"
    code_type = "native"
    language = "bash"
    execution_methods = ["command"]

    @staticmethod
    def code(task):
        if task.device.os == "windows":
            return "net user"
        else:
            return "cat /etc/passwd"
