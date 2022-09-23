import os

import tomli
import tomli_w


def load_config() -> dict:
    """Load the config.toml file"""
    try:
        with open(os.getenv("PHOENIX_CONFIG_PATH"), "rb") as f:
            return tomli.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The config file ({os.getenv('PHOENIX_CONFIG_PATH')}) doesn't exist.") from e
    except tomli.TOMLDecodeError:
        raise tomli.TOMLDecodeError(f"The config file ({os.getenv('PHOENIX_CONFIG_PATH')}) is an invalid format.")
def dump_config(config: dict):
    """Dump the updated config"""
    with open(os.getenv("PHOENIX_CONFIG_PATH"), "wb") as f:
        tomli_w.dump(config, f)
