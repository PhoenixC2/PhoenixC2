import os

import tomllib
import tomli_w

from .resources import get_resource


def load_config() -> dict:
    """Load the config from the config file."""
    name = os.getenv("PHOENIX_CONFIG", "default") + ".toml"
    config = get_resource("data/configs", name)
    if not os.path.exists(config):
        raise FileNotFoundError(f"Config file '{name}' does not exist.")

    with config.open("rb") as f:
        return tomllib.load(f)


def save_config(config: dict, name: str = None) -> None:
    """Save the updated config to the config file."""
    if name is None:
        name = os.getenv("PHOENIX_CONFIG", "default") + ".toml"
    config_file = get_resource("data/configs/", name)
    with config_file.open("wb") as f:
        tomli_w.dump(config, f)
