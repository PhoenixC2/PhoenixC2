"""Reverse Socket TCP Listener"""
import netifaces

class Listener():
    """The Reverse Tcp Listener Class"""
    # Will be shown by Frontend
    # On create dictionary containing these exact keys will be saved to database as config
    # If default is None, user has to specify his own
    # If required can't be left out
    options = {
        "ssl": {
            "type": "bool",
            "required": False,
            "default": False
        },
        "connection_limit": {
            "type": "int",
            "required": False,
            "default": 5
        },
        "address": {
            "type": "str",
            "required": False,
            "default": "0.0.0.0"
        },
        "port": {
            "type": "int",
            "required": False,
            "default": "0.0.0.0"
        },
        "webhook":  {
            "type": "url",
            "required": False,
            "default": None
        },
    }
