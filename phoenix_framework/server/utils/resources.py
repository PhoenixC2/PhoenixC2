import os
import subprocess

from importlib_resources import files
from importlib_resources.abc import Traversable


def get_resource(
    path: str, file: str = None, skip_file_check: bool = False
) -> Traversable:
    """Get the resource from a path."""
    if path[-1] == "/":
        path = path[:-1]
    if file is not None:
        resource = files("phoenix_framework.server." + path.replace("/", ".")).joinpath(
            file
        )
    else:
        resource = files("phoenix_framework.server." + path.replace("/", "."))
    if os.path.exists(str(resource)) or skip_file_check:
        return resource
    else:
        raise FileNotFoundError(f"Resource '{file}' does not exist.")
