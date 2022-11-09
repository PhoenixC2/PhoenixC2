import os

from importlib_resources import files
from importlib_resources.abc import Traversable

kits_dir = files("phoenix_frameworks.server.kits")
print(kits_dir.joinpath("http-reverse/listener.py").exists())
