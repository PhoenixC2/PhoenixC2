import base64
from phoenixc2.server.bypasses.base import BaseBypass


class Bypass(BaseBypass):
    name = "Base64"
    description = "Base64 encoder"
    os = ("windows", "linux", "macos")

    def generate(self, stager, args):
        final_payload = stager.stager_class.generate(stager)

        if final_payload.payload.compiled:
            raise Exception("Cannot encode compiled payloads")

        return base64.b64encode(final_payload.output.encode()).decode()
