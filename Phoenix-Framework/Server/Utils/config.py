import tomli
import tomli_w


def load_config(config_path: str) -> dict:
    """Load the config.toml file"""
    with open(config_path, "rb") as f:
        return tomli.load(f)
def dump_config(config_path : str, config: dict):
    """Dump the updated config"""
    with open(config_path, "wb") as f:
        tomli_w.dump(config, f)
