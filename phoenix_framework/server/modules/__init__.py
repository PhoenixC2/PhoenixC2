import importlib
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import BaseModule


def get_module(name: str) -> "BaseModule":
    """Get a module by name."""
    return importlib.import_module(f"Modules.{name.replace('/', '.')}").Module


def get_all_module_paths():
    file_paths = []

    # Walk the tree.
    for root, directories, files in os.walk("Modules"):
        for filename in files:
            # check that the root is not __pycache__ or the parent directory
            if (
                "__pycache__" in root
                or "base.py" in filename
                or "__init__.py" in filename
            ):
                print("lol")
                continue
            filepath = os.path.join(root, filename)
            file_paths.append(filepath.replace("Modules/", ""))

    return file_paths
