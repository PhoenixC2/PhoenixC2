import importlib
from .base import BaseBypass
from phoenixc2.server.utils.resources import get_resource

IGNORE = ("__pycache__",)


def get_bypass(category: str, name: str) -> "BaseBypass":
    """Get a bypass by category and name."""
    return importlib.import_module(
        f"phoenixc2.server.bypasses.{category}.{name}"
    ).Bypass()


def get_all_bypasses() -> dict[str, list[str]]:
    bypasses: dict[str, list[str]] = {}

    # Walk the tree.
    for file in get_resource("bypasses").iterdir():
        if file.is_dir() and file.name not in IGNORE:
            bypasses[file.name] = []
            for sub_file in file.iterdir():
                if sub_file.is_file():
                    bypasses[file.name].append(sub_file.stem)

    return bypasses
