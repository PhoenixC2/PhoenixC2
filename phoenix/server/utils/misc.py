import platform
from typing import TYPE_CHECKING
from uuid import uuid1

import netifaces

version = "0.1"


def get_network_interfaces() -> dict[str, str]:
    """Get address of all network interfaces on the host"""
    interfaces = {"all": "0.0.0.0"}
    for interface in netifaces.interfaces():
        ifaddresses = netifaces.ifaddresses(interface)
        if ifaddresses.get(2) is not None:  # checks if addr is available
            interfaces[interface] = ifaddresses[2][0]["addr"]
    return interfaces


def get_platform() -> str:
    """Get the platform of the host"""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Linux":
        return "linux"
    elif system == "Darwin":
        return "osx"
    else:
        return "unknown"
