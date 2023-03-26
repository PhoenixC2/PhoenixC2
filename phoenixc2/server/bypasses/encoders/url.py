from urllib.parse import quote
from phoenixc2.server.bypasses.base import BaseBypass


class Bypass(BaseBypass):
    name = "Url"
    description = "Url Encoder"
    supported_languages = ("python",)

    def generate_body(self, final_payload, args):
        final_payload.output = quote(final_payload.output)
        return final_payload

    def generate(self, final_payload, args):
        if final_payload.payload.compiled:
            raise Exception("Cannot encode compiled payloads")

        if final_payload.payload.language == "python":
            self.python_wrapper(final_payload, args)

        return final_payload

    def python_wrapper(self, final_payload, args):
        final_payload.output = (
            'import urllib.parse;exec(urllib.parse.unquote("'
            + self.generate_body(final_payload, args).output
            + '"))'
        )
        return final_payload
