import os
from typing import TYPE_CHECKING
import shlex
import jinja2

from phoenixc2.server.utils.options import (
    AddressType,
    Option,
    OptionPool,
    StringType,
    DefaultStagerPool,
    IntegerType,
)
from phoenixc2.server.utils.resources import get_resource

from phoenixc2.server.utils.features import Feature
from ..stager_base import BaseStager
from ..payload_base import BasePayload, FinalPayload

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
    language = "python"
    end_format = "py"
    compiled = False
    option_pool = OptionPool()

    @classmethod
    def generate(
        cls, stager_db: "StagerModel", recompile: bool = False
    ) -> "FinalPayload":
        jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )
        template = jinja2_env.get_template("payloads/python.payload.py")

        final_payload = FinalPayload(cls, stager_db)
        final_payload.set_output_from_content(template.render(stager=stager_db))
        return final_payload


class GoPayload(BasePayload):
    name = "Golang Payload"
    description = "Compiled cross-platform Golang Payload"
    module_execution_methods = [
        "command",
    ]
    module_code_types = []
    module_languages = ["bash"]
    language = "go"
    end_format = ".exe"
    compiled = True
    option_pool = OptionPool(
        [
            Option(
                name="Operating System",
                description="The operating system to compile for",
                real_name="os",
                type=StringType(),
                default="windows",
                required=True,
            ),
            Option(
                name="Architecture",
                description="The architecture to compile for",
                real_name="arch",
                type=StringType(),
                default="amd64",
                required=True,
            ),
        ]
    )
    features = [
        Feature(
            name="Cross-Platform",
            description="The payload can be compiled for multiple platforms",
            pro=True,
        )
    ]

    @classmethod
    def generate(cls, stager_db, recompile=False):
        if cls.already_compiled(stager_db) and not recompile:
            final_payload = FinalPayload(
                cls,
                stager_db,
            )
            final_payload.set_output_from_path(
                cls.get_output_file(stager_db),
            )
            return final_payload

        jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )
        template = jinja2_env.get_template("payloads/go.go")
        output = template.render(stager=stager_db)

        # write to file
        go_file = get_resource(
            "data/stagers/", f"{stager_db.id}.go", skip_file_check=True
        )
        output_file = cls.get_output_file(stager_db)

        with go_file.open("w") as f:
            f.write(output)

        # compile
        operation_system = shlex.quote(stager_db.options["os"])
        architecture = shlex.quote(stager_db.options["arch"])

        status_code = os.system(
            f"GOOS={operation_system} GOARCH={architecture} go build"
            f" -o {output_file} {go_file}"
        )
        # remove go file
        # go_file.unlink()

        if status_code != 0:
            raise Exception("Failed to compile")

        final_payload = FinalPayload(
            cls,
            stager_db,
        )
        final_payload.set_output_from_path(output_file)
        return final_payload


class Stager(BaseStager):
    name = "http-reverse"
    description = "Reverse HTTP(S) stager"
    author: str = "Screamz2k"
    payloads = {"python": PythonPayload, "go": GoPayload}
    option_pool = DefaultStagerPool(
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
                default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
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
