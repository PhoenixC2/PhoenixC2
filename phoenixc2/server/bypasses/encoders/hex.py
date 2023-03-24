from phoenixc2.server.bypasses.base import BaseBypass


class Bypass(BaseBypass):
    name = "Hex"
    description = "Hex Encoder"
    os = ("windows", "linux", "macos")

    def generate(self, stager, args):
        final_payload = stager.stager_class.generate(stager)

        if final_payload.payload.compiled:
            raise Exception("Cannot encode compiled payloads")

        return final_payload.output.encode().hex()
