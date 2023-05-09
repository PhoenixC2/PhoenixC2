import base64
from phoenixc2.server.bypasses.base import BaseBypass


class Bypass(BaseBypass):
    name = "Base64"
    description = "Base64 encoder"
    author = "screamz2k"
    supported_languages = ("python",)

    def generate_body(self, final_payload, args):
        return base64.b64encode(final_payload.output.encode()).decode()

    def generate(self, final_payload, args):
        if final_payload.payload.compiled:
            raise Exception("Cannot encode compiled payloads")

        if final_payload.payload.language == "python":
            self.python_wrapper(final_payload, args)

        return final_payload

    def python_wrapper(self, final_payload, args):
        final_payload.output = (
            'import base64;exec(base64.b64decode("'
            + self.generate_body(final_payload, args)
            + '").decode())'
        )
        return final_payload
