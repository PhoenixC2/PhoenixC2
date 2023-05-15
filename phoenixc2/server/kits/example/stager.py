from phoenixc2.server.kits.payload_base import FinalPayload

from phoenixc2.server.utils.options import (
    DefaultStagerPool,
    Option,
    OptionPool,
    StringType,
)

from ..stager_base import BasePayload, BaseStager


class ExamplePayload(BasePayload):
    supported_target_os = ["linux", "windows", "osx"]
    supported_target_arch = ["x64", "x86"]
    supported_server_os = ["linux", "windows"]
    compiled = False
    options = OptionPool()

    @classmethod
    def generate(cls, stager_db, recompile=False, uid_tracking=False):
        print("Generating example payload")
        final_payload = FinalPayload(cls, stager_db)
        final_payload.set_output_from_content("Example Payload Content")
        return final_payload


class Stager(BaseStager):
    name = "example"
    description = "Example Stager"
    options = DefaultStagerPool(
        [
            Option(
                name="Example Option",
                description="Example Option Description",
                type=StringType(),
                default="Example Default Value",
                required=True,
            )
        ]
    )
    payloads = {"example": ExamplePayload}
