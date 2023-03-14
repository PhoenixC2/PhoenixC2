import os

from importlib_resources import files
from importlib_resources.abc import Traversable

PICTURES = "data/pictures/"


def get_resource(
    path: str, file: str = None, skip_file_check: bool = False
) -> Traversable:
    """Get the resource from a path."""
    # remove the first slash if it exists
    if path[-1] == "/":
        path = path[:-1]

    # check if file is given
    if file is not None:
        resource = files("phoenixc2.server." + path.replace("/", ".")).joinpath(file)
    else:
        resource = files("phoenixc2.server." + path.replace("/", ".")).joinpath("")

    # check if file or directory exists if skip_file_check is False
    if os.path.exists(str(resource)) or skip_file_check:
        return resource
    else:
        raise FileNotFoundError(f"Resource '{file}' does not exist.")
