import importlib
import os
from typing import TYPE_CHECKING

from phoenixc2.server.utils.resources import get_resource

if TYPE_CHECKING:
    from .base import BaseModule


def get_module(path: str) -> "BaseModule":
    """Get a module by name."""
    return importlib.import_module(
        f"phoenixc2.server.modules.{path.replace('/', '.')}.module"
    ).Module()


def get_all_module_paths():
    """Get all module paths."""
    file_paths = []

    # Walk the tree.
    for root, directories, files in os.walk(str(get_resource("modules", ""))):
        for filename in files:
            # check that the root is not __pycache__ or the parent directory
            if (
                "__pycache__" in root
                or "base.py" in filename
                or "__init__.py" in filename
            ):
                continue
            filepath = os.path.join(root, filename)
            # only show path after modules directory and remove module.py
            file_paths.append(
                filepath.split("modules")[1][1:].replace("module.py", "")[:-1]
            )

    return file_paths
