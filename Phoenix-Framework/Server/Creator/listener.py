"""Create Listeners"""
import importlib
import time
from typing import Optional

from Commander import Commander
from Database import ListenerModel, Session
from Listeners.base import BaseListener

from .available import AVAILABLE_LISTENERS


def add_listener(data: dict) -> str:
    """
    Create a listener

    :param type: The type of listener
    :param name: The name of the listener
    :param address: The address of the listener
    :param port: The port of the listener
    :return: status

    """
    # Check if name is already in use
    name = data["name"]
    if Session.query(ListenerModel).filter_by(name=name).first() is not None:
        raise ValueError(f"Listener {name} already exists.")

    listener = ListenerModel.create_listener_from_data(data)
    Session.add(listener)
    Session.commit()
    return f"Created '{name}' successfully!"


def start_listener(listener_db: ListenerModel, commander: Commander) -> Optional[str]:
    """
    Start a listener

    :param listener_id: The ID of the listener
    :param commander: The main commander
    :return: Status

    """

    # Check if Listener is already active
    try:
        commander.get_active_listener(listener_db.id)
    except Exception:
        pass
    else:
        raise ValueError("Listener is already active!") from None

    # Get the Listener from the File
    listener =  listener_db.create_listener_object(commander)

    # Start Listener
    listener.start()
    commander.add_active_listener(listener)
    return f"Started Listener with ID {listener_db.id}"


def stop_listener(listener_db: ListenerModel, commander: Commander) -> None:
    """
    Stop a listener

    :param listener_id: The ID of the listener
    :param commander: The main commander

    """
    listener = commander.get_active_listener(listener_db.id)
    listener.stop()
    commander.remove_listener(listener_db.id)

def restart_listener(listener_db: ListenerModel, commander: Commander) -> None:
    """
    Restart a listener
    
    :param listener_id: The ID of the listener
    :param commander: The main commander
    """
    stop_listener(listener_db, commander)
    time.sleep(5)
    start_listener(listener_db, commander)
