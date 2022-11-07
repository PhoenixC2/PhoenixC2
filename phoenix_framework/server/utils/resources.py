import subprocess
import os
from importlib_resources import files
from importlib_resources.abc import Traversable


def get_resource(path: str, file: str) -> Traversable:
    """Get the resource from a path."""
    resource = files("phoenix_framework.server." + path.replace("/", ".")).joinpath(file)
    if resource.exists():
        return resource
    else:
        raise FileNotFoundError(f"Resource '{file}' does not exist.")


def regenerate_ssl():
    """Generate the ssl certificates."""

    ssl_cert = get_resource("server/data", "ssl.pem")
    ssl_key = get_resource("server/data", "ssl.key")

    # check if the ssl certificates exist and delete them
    if not os.path.exists(ssl_cert):
        os.remove(ssl_cert)
    if not os.path.exists(ssl_key):
        os.remove(ssl_key)
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:4096",
            "-keyout",
            ssl_key,
            "-out",
            ssl_cert,
            "-days",
            "365",
            "-nodes",
            "-subj",
            "/CN=US",
        ],
        check=True,
    )


def create_directories():
    """Create the directories for the server where the data is stored."""
    for dir in ["stagers", "downloads", "uploads"]:
        if not os.path.exists(get_resource("server/data", dir)):
            os.makedirs(get_resource("server/data", dir))
