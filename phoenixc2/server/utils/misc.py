import platform
from datetime import datetime
from uuid import uuid1
from psutil import net_if_addrs

def get_network_interfaces() -> dict[str, str]:
    """Get address of all network interfaces on the host"""
    interfaces = {"all": "0.0.0.0"}
    for interface_name, interface_addresses in net_if_addrs().items():
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET':
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


def format_datetime(date_time: datetime) -> str:
    if date_time is None:
        return ""
    if datetime.now() > date_time:
        time_difference = datetime.now() - date_time
        if time_difference.days > 0:
            seconds = time_difference.seconds + (time_difference.days * 86400)
        else:
            seconds = time_difference.seconds
        if seconds < 5:
            return "now"
        if seconds < 60:
            return f"{time_difference.seconds} seconds ago"
        elif seconds < 3600:
            return f"{seconds // 60} minute{'s' if seconds // 60 > 1 else ''} ago"
        elif time_difference.days == 0:
            return f"{seconds // 3600} hour{'s' if seconds // 3600 > 1 else ''} ago"
        elif time_difference.days == 1:
            return "yesterday"
        elif time_difference.days < 7:
            return f"{time_difference.days} day{'s' if time_difference.days > 1 else ''} ago"
        elif time_difference.days <= 31:
            return f"{time_difference.days // 7} week{'s' if time_difference.days // 7 > 1 else ''} ago"
        else:
            return date_time.strftime("%d/%m/%Y")
    else:
        time_difference = date_time - datetime.now()
        if time_difference.days > 0:
            seconds = time_difference.seconds + (time_difference.days * 86400)
        else:
            seconds = time_difference.seconds
        if seconds < 5:
            return "now"
        if seconds < 60:
            return f"in {time_difference.seconds} seconds"
        elif seconds < 3600:
            return f"in {seconds // 60} minute{'s' if seconds // 60 > 1 else ''}"
        elif time_difference.days == 0:
            return f"in {seconds // 3600} hour{'s' if seconds // 3600 > 1 else ''}"
        elif time_difference.days == 1:
            return "tomorrow"
        elif time_difference.days < 7:
            return f"in {time_difference.days} day{'s' if time_difference.days > 1 else ''}"
        elif time_difference.days <= 31:
            return f"in {time_difference.days // 7} week{'s' if time_difference.days // 7 > 1 else ''}"
        else:
            return date_time.strftime("%d/%m/%Y")

class Status():
    """Indicates the response status of a request or action"""
    Success = "success"
    Danger = "danger"
    Error = "danger" # Alias
    Warning = "warning"
    Info = "info"
    Alert = "alert"
    Critical = "critical"