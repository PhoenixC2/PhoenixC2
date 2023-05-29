import os
import shutil
import subprocess
from typing import TYPE_CHECKING
import jinja2
import tempfile

from phoenixc2.server.utils.options import (
    ChoiceType,
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
    file_ending = ".py"
    compiled = False
    option_pool = OptionPool()
    features = [
        Feature(
            name="Cross-Platform",
            description="The payload can be compiled for multiple platforms",
            pro=True,
        ),
        Feature(
            name="Requires Python",
            description="The payload requires python and the dependencies"
            " to be installed on the target",
            pro=False,
        ),
    ]

    @classmethod
    def generate(
        cls, stager_db: "StagerModel", recompile: bool = False, identifier=None
    ) -> "FinalPayload":
        jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )
        template = jinja2_env.get_template("payloads/python.payload.py")

        final_payload = FinalPayload(cls, stager_db)
        final_payload.set_output_from_content(
            template.render(stager=stager_db, identifier=identifier)
        )
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
    file_ending = ".exe"
    compiled = True
    option_pool = OptionPool(
        [
            Option(
                name="Operating System",
                description="The target operating system",
                real_name="os",
                type=ChoiceType(
                    ["windows", "linux", "darwin", "freebsd", "netbsd", "openbsd"], str
                ),
                default="windows",
                required=True,
            ),
            Option(
                name="Architecture",
                description="The architecture to compile for",
                real_name="arch",
                type=ChoiceType(["amd64", "386", "arm", "arm64"], str),
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
    required_applications = ["go"]

    @classmethod
    def generate(cls, stager_db, recompile=False, identifier=None):
        if cls.already_compiled(stager_db) and not recompile:
            final_payload = FinalPayload(
                cls,
                stager_db,
            )
            if stager_db.options["os"] == "linux":
                final_payload.file_ending = ""
            final_payload.set_output_from_path(
                cls.get_output_file(stager_db),
            )
            return final_payload

        cls.check_for_required_applications()

        jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )

        # create temp dir
        temp_dir = tempfile.TemporaryDirectory()

        # copy go package to temp dir
        shutil.copytree(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "payloads", "golang_payload"
            ),
            os.path.join(temp_dir.name, "golang_payload"),
        )

        # overwrite main.go
        go_file = os.path.join(
            temp_dir.name, "golang_payload", "cmd", "executable", "main.go"
        )
        with open(go_file, "w") as f:
            f.write(
                jinja2_env.get_template(
                    "payloads/golang_payload/cmd/executable/main.go"
                ).render(stager=stager_db, identifier=identifier)
            )

        # get output file
        output_file = cls.get_output_file(stager_db)

        # compile
        os.environ["GOOS"] = stager_db.options["os"]
        os.environ["GOARCH"] = stager_db.options["arch"]
        os.environ["CGO_ENABLED"] = "0"

        process = subprocess.run(
            ["go", "build", "-ldflags", "-s -w", "-o", str(output_file), go_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=temp_dir.name + "/golang_payload",
        )

        # remove go file (comment out for debugging)
        os.unlink(go_file)

        # remove temp dir
        temp_dir.cleanup()

        if process.returncode != 0:
            raise Exception("Failed to compile")

        final_payload = FinalPayload(
            cls,
            stager_db,
        )
        if stager_db.options["os"] == "linux":
            final_payload.file_ending = ""

        final_payload.set_output_from_path(output_file)
        return final_payload


class GoDllPayload(BasePayload):
    name = "Golang DLL Payload"
    description = "Compiled cross-platform Golang DLL Payload"
    module_execution_methods = [
        "command",
    ]
    module_code_types = []
    module_languages = ["bash"]
    language = "go"
    file_ending = ".dll"
    compiled = True
    option_pool = OptionPool(
        [
            Option(
                name="Architecture",
                description="The architecture to compile for",
                real_name="arch",
                type=ChoiceType(["amd64", "386", "arm", "arm64"], str),
                default="amd64",
                required=True,
            ),
            Option(
                name="Exported function",
                description="Name of the exported function",
                real_name="exported_function",
                type=StringType(),
                default="Execute",
                required=True,
            ),
        ]
    )
    features = [
        Feature(
            name="Cross-Platform",
            description="The payload can be compiled for multiple platforms",
            pro=True,
        ),
        Feature(
            name="DLL",
            description="The payload is a DLL and can be injected into other processes",
            pro=True,
        ),
    ]
    required_applications = ["x86_64-w64-mingw32-gcc", "i686-w64-mingw32-gcc", "go"]

    @classmethod
    def generate(cls, stager_db, recompile=False, identifier=None):
        if cls.already_compiled(stager_db) and not recompile:
            final_payload = FinalPayload(
                cls,
                stager_db,
            )
            final_payload.set_output_from_path(
                cls.get_output_file(stager_db),
            )
            return final_payload

        cls.check_for_required_applications()  # check for required applications

        jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )

        # create temp dir
        temp_dir = tempfile.TemporaryDirectory()

        # copy go package to temp dir
        shutil.copytree(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "payloads", "golang_payload"
            ),
            os.path.join(temp_dir.name, "golang_payload"),
        )

        # overwrite main.go
        go_file = os.path.join(temp_dir.name, "golang_payload", "cmd", "dll", "main.go")
        with open(go_file, "w") as f:
            f.write(
                jinja2_env.get_template(
                    "payloads/golang_payload/cmd/dll/main.go"
                ).render(
                    stager=stager_db,
                    identifier=identifier,
                )
            )

        # get output file
        output_file = cls.get_output_file(stager_db)

        os.environ["GOOS"] = "windows"
        os.environ["GOARCH"] = stager_db.options["arch"]
        os.environ["CGO_ENABLED"] = "1"

        if stager_db.options["arch"] == "i386":
            os.environ["CC"] = "i686-w64-mingw32-gcc"
        else:
            os.environ["CC"] = "x86_64-w64-mingw32-gcc"

        ldflags = ["-s", "-w", "-H=windowsgui"]
        result = subprocess.run(
            [
                "go",
                "build",
                "-buildmode=c-shared",
                "-ldflags=" + " ".join(ldflags),
                "-o",
                str(output_file),
                str(go_file),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=temp_dir.name + "/golang_payload",
        )

        # remove temp dir
        temp_dir.cleanup()

        if result.returncode != 0:
            raise Exception("Failed to compile")

        # remove header if it exists
        get_resource("data/stagers/", f"{stager_db.id}.h", skip_file_check=True).unlink(
            missing_ok=True
        )

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
    payloads = {"python": PythonPayload, "go": GoPayload, "go_dll": GoDllPayload}
    option_pool = DefaultStagerPool(
        [
            Option(
                name="Sleep Time",
                description="The time to sleep between each request."
                " Should be less than the listener timeout.",
                real_name="sleep-time",
                type=IntegerType(),
                default=5,
                required=True,
            ),
            Option(
                name="Request User-Agent",
                real_name="user-agent",
                description="The User-Agent to use for the requests.",
                type=StringType(),
                default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            ),
        ],
        list(payloads.keys()),
    )
