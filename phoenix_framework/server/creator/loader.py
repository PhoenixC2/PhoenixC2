"""Create Loaders to download the stager and execute it."""
from phoenix_framework.server.database import Session, StagerModel


def create_loader(stager_id: int, format: str, encoding: str):
    """
    Create a Loader for a specific stager
    Args:
        :param stager_id: The ID of the stager
        :param format: The format of the loader
        :param encoding: The encoding of the loader
    Returns:
        :string: the loader
    """
    # Check if stager exists
    stager = Session.query(StagerModel).filter_by(id=stager_id)
    if stager is None:
        raise ValueError(f"Stager with ID {stager_id} does not exist")

    # Check if language is valid
    if format not in [
        "python",
        "powershell",
        "php",
        "java",
        "batch",
        "php",
        "javascript",
        "shell",
    ]:
        raise ValueError(f"Format {format} is not supported")

    # Create Loader
    # Encode Loader
    return "Loader"