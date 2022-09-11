import netifaces

version = "0.1"


def get_network_interfaces() -> dict[str, str]:
    """Get address of all network interfaces on the host"""
    interfaces = {}
    for interface in netifaces.interfaces():
        ifaddresses = netifaces.ifaddresses(interface)
        if ifaddresses.get(2) is not None:  # checks if addr is available
            interfaces[interface] = ifaddresses[2][0]["addr"]
    return interfaces
