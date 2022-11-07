import os
from importlib_resources import files
from importlib_resources.abc import Traversable

data_dir = files("phoenix_frameworks.server.data")
ssl_cert = data_dir.joinpath("ssl.pemoiuhsau")

print(ssl_cert.exists())