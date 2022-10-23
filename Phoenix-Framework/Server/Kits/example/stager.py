import os
from typing import TYPE_CHECKING

import jinja2
from Utils.options import DefaultStagerPool, Option, OptionPool, StringType

from ..base_stager import BasePayload, BaseStager, FinalPayload

if TYPE_CHECKING:
    from Database import StagerModel


class ExamplePayload(BasePayload):
    supported_target_os = ["linux", "windows", "osx"]
    supported_target_arch = ["x64", "x86"]
    supported_server_os = ["linux", "windows"]
    compiled = False
    options = OptionPool()

    @staticmethod
    def generate(stager_db: "StagerModel") -> FinalPayload:
        print("Generating example payload")

class Stager(BaseStager):
    name = "example"
    description = "Example Stager"
    options = DefaultStagerPool([
        Option(
            name="Example Option",
            description="Example Option Description",
            type=StringType(),
            default="Example Default Value",
            required=True
        )
    ])
    payloads = {
        "example": ExamplePayload
    }

    def generate(self, stager_db: "StagerModel") -> tuple[bytes | str, bool]:
        if stager_db.payload_type not in self.payloads:
            raise ValueError("Invalid payload type")

        return self.payloads[stager_db.payload_type].generate(stager_db)
