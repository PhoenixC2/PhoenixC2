import os
from phoenixc2.server.utils.resources import get_resource


def get_all_kits() -> list[str]:
    """Get all kits"""
    kits = []
    # Walk the tree.
    for dir in os.listdir(str(get_resource("kits", ""))):
        # check that the root is not __pycache__ or the parent directory
        if dir in ["__pycache__", "example"] or not os.path.isdir(
            str(get_resource("kits", dir))
        ):
            continue
        # only show path after modules directory and remove module.py
        kits.append(dir)

    return kits
