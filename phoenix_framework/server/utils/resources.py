import os
import subprocess

from importlib_resources import files
from importlib_resources.abc import Traversable


def get_resource(path: str, file: str, skip_file_check: bool = False) -> Traversable:
    """Get the resource from a path."""
    if path[-1] == "/":
        path = path[:-1]
    resource = files("phoenix_framework.server." + path.replace("/", ".")).joinpath(
        file
    )
    if resource.exists() or skip_file_check:
        return resource
    else:
        raise FileNotFoundError(f"Resource '{file}' does not exist.")
