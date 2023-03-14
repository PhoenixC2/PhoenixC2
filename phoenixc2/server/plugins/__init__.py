import importlib


def get_plugin(name):
    """Get a plugin by name."""
    try:
        return importlib.import_module(
            f"phoenixc2.server.plugins.{name}.plugin"
        ).Plugin()
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"Plugin '{name}' not found.")
