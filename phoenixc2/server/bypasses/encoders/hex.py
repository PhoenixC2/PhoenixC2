from phoenixc2.server.bypasses.base import BaseBypass


class Bypass(BaseBypass):
    name = "Hex"
    description = "Hex Encoder"
    author = "screamz2k"
    supported_languages = ("python",)

    def generate_body(self, final_payload, args):
        return final_payload.output.encode().hex()

    def generate(self, final_payload, args):
        if final_payload.payload.compiled:
            raise Exception("Cannot encode compiled payloads")

        if final_payload.payload.language == "python":
            self.python_wrapper(final_payload, args)

        return final_payload

    def python_wrapper(self, final_payload, args):
        final_payload.output = (
            'import codecs;exec(codecs.decode("'
            + self.generate_body(final_payload, args)
            + '", "hex"))'
        )
        return final_payload
