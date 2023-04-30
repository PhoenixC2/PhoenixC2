import platform
from uuid import uuid1
from psutil import net_if_addrs


def get_network_interfaces() -> dict[str, str]:
    """Get address of all network interfaces on the host"""
    interfaces = {"all": "0.0.0.0"}
    for interface_name, interface_addresses in net_if_addrs().items():
        for address in interface_addresses:
            if str(address.family) == "2":
                interfaces[interface_name] = address.address
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


def generate_name() -> str:
    """Generate a random name"""
    return str(uuid1())[:8]


class Status:
    """Indicates the response status of a request or action"""

    Success = "success"
    Danger = "danger"
    Error = "danger"  # Alias
    Warning = "warning"
    Info = "info"
    Alert = "alert"
    Critical = "critical"
