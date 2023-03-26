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
from ..base_stager import BaseStager
from ..base_payload import BasePayload, FinalPayload

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
        template = jinja2_env.get_template("payloads/python.j2")
        output = template.render(stager=stager_db)

        return FinalPayload(cls, stager_db, output)


class GoPayload(BasePayload):
    name = "Golang Payload"
    description = "Compiled cross-platform Golang Payload"
    module_execution_methods = []
    module_code_types = []
    module_languages = []
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
    def is_compiled(cls, stager_db: "StagerModel") -> bool:
        try:
            get_resource(
                "data/stagers/",
                f"{stager_db.name}.exe",
            )
        except FileNotFoundError:
            return False
        return True

    @classmethod
    def generate(
        cls, stager_db: "StagerModel", recompile: bool = False
    ) -> "FinalPayload":
        if cls.is_compiled(stager_db) and not recompile:
            return FinalPayload(
                cls,
                stager_db,
                get_resource(
                    "data/stagers/",
                    f"{stager_db.name}.exe",
                ),
            )

        jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )
        template = jinja2_env.get_template("payloads/go.j2")
        output = template.render(stager=stager_db)

        # write to file
        go_file = get_resource(
            "data/stagers/", f"{stager_db.name}.go", skip_file_check=True
        )
        executable = get_resource(
            "data/stagers/", f"{stager_db.name}.exe", skip_file_check=True
        )

        with go_file.open("w") as f:
            f.write(output)

        # compile
        operation_system = shlex.quote(stager_db.options["os"])
        architecture = shlex.quote(stager_db.options["arch"])

        status_code = os.system(
            f"GOOS={operation_system} GOARCH={architecture} go build"
            f"-o {executable} {go_file}"
        )
        # remove go file
        go_file.unlink()
        os.unlink
        if status_code != 0:
            raise Exception("Failed to compile")

        return FinalPayload(
            cls,
            stager_db,
            executable.open("rb"),
        )


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
