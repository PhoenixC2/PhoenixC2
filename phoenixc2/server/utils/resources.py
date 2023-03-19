from importlib.resources import files
from pathlib import Path

PICTURES = "data/pictures/"


def get_resource(
    root: str, path_after: str = "", skip_file_check: bool = False
) -> Path:
    """Get the resource from a path.

    Args:
        root (str): The root path.
        path_after (str, optional): The path after the root path. Defaults to "" which returns the root path.
        skip_file_check (bool, optional): Skip the file check. Defaults to False.

    Returns:
        Path: The path to the resource.
    """
    # remove the first slash if it exists
    if root[-1] == "/":
        root = root[:-1]

    # check if file is given
    resource = files("phoenixc2.server." + root.replace("/", ".")).joinpath(path_after)

    # check if file exists
    if resource.exists() or skip_file_check:
        return resource
    else:
        raise FileNotFoundError()
