import os
from ..base_stager import BaseStager
from Utils.options import DefaultStagerPool, Option, StringType, AddressType, IntegerType, ChoiceType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Database import StagerModel


class Stager(BaseStager):
    option_pool = DefaultStagerPool([
        Option(
            name="Type",
            description="The type of stager to generate",
            type=ChoiceType([x.split(".")[0] for x in os.listdir("Server/Kits/http-reverse/payloads/")]),
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

    def generate_stager(self, stager_db: "StagerModel") -> tuple[bytes | str, bool]: 
        if stager_db.options["type"] == "python":
            with open("Server/Kits/http-reverse/payloads/python.py", "r") as f:
                stager = f.read()
                
                return f.read().replace("{{HOST}}", stager_db.listener.address).replace("{{PORT}}", str(stager_db.listener.port)), False