import os
from phoenixc2.server.utils.resources import get_resource


def get_all_kits() -> list[str]:
    """Get all kits"""
    kits = []
    # Walk the tree.
    for file_or_dir in os.listdir(str(get_resource("kits", ""))):
        # check that the root is not __pycache__ or the parent directory
        if file_or_dir in [
            "__pycache__",
            "example",
            "__init__.py",
        ] or not os.path.isdir(str(get_resource("kits", file_or_dir))):
            continue
        # only show path after modules directory and remove module.py
        kits.append(file_or_dir)

    return kits
