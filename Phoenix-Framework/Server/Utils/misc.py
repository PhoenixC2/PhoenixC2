from typing import TYPE_CHECKING

import netifaces
from Database import LogEntryModel, Session, UserModel

version = "0.1"


def get_network_interfaces() -> dict[str, str]:
    """Get address of all network interfaces on the host"""
    interfaces = {}
    for interface in netifaces.interfaces():
        ifaddresses = netifaces.ifaddresses(interface)
        if ifaddresses.get(2) is not None:  # checks if addr is available
            interfaces[interface] = ifaddresses[2][0]["addr"]
    return interfaces
def log_to_database(alert: str, description: str, user: "UserModel"=None) -> LogEntryModel:
    log = LogEntryModel.generate_log(alert, description, Session.query(UserModel).all(), user)
    Session.add(log)
    Session.commit()
    return log