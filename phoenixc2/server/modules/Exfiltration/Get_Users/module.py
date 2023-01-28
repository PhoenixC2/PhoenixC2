from phoenixc2.server.modules.base import BaseModule


class Module(BaseModule):
    name = "Get_Users"
    description = "Get all users on the system."

    def code(self, device, task):
        if device.os == "windows":
            return """
            import subprocess

            os.system("net user")
            """
        else:
            return """
            import subprocess

            os.system("cat /etc/passwd")
            """
