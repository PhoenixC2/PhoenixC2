from importlib.resources import path

PICTURES = "data/pictures/"


def get_resource(root: str, path_after: str = "", skip_file_check: bool = False):
    """Get the resource from a path."""
    # remove the first slash if it exists
    if root[-1] == "/":
        root = root[:-1]

    # check if file is given
    resource = path("phoenixc2.server." + root.replace("/", "."), path_after)

    # check if file exists
    if resource.exists() or skip_file_check:
        return resource
    else:
        raise FileNotFoundError()
