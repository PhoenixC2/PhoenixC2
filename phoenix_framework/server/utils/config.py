import os
import tomli
import tomli_w
from .resources import get_resource

def load_config(name: str) -> dict:
    """Load the config from the config file."""
    config = get_resource("server/data/configs/", name)
    if not os.path.exists(config):
        raise FileNotFoundError(f"Config file '{name}' does not exist.")
    
    with config.open() as f:
        return tomli.load(f)

def save_config(name: str, config: dict):
    """Save the updated config to the config file."""
    config = get_resource("server/data/configs/", name)
    with config.open("w") as f:
        return tomli_w.dump(config, f)