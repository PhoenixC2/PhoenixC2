"""Create Listeners"""
import importlib
import time
from typing import Optional

from Commander.commander import Commander
from Database import ListenerModel, db_session
from Listeners.base import BaseListener

from .options import AVAILABLE_LISTENERS


def add_listener(listener_type: str = None,
                    name: str = None,
                    address: str = None,
                    port: int = None,
                    ssl: bool = False,
                    connection_limit: int = 5) -> str:
    """
    Create a listener

    :param type: The type of listener
    :param name: The name of the listener
    :param address: The address of the listener
    :param port: The port of the listener
    :return: status

    """
    # Check if Listener exists
    if db_session.query(ListenerModel).filter_by(name=name).first():
        raise Exception(f"Listener {name} already exists.")

    # Check if type is valid
    if listener_type[0] == "/":
        listener_type = listener_type[1:]

    if listener_type not in AVAILABLE_LISTENERS:
        raise Exception(f"Listener {listener_type} is not available.")
    try:
        open("Listeners/" + listener_type + ".py", "r").close()
    except:
        raise Exception(f"Listener {listener_type} does not exist") from None

    # Save Listener
    listener = ListenerModel(name=name,
                             type=listener_type,
                             address=address,
                             port=port,
                             ssl=ssl,
                             connection_limit=connection_limit)
    db_session.add(listener)
    db_session.commit()
    return f"Listener {name} created"


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
    except:
        pass
    else:
        raise Exception("Listener is already active!") from None

    # Get the Listener from the File
    listener =  listener_db.create_listener(commander)

    # Start Listener
    try:
        listener.start()
        commander.add_active_listener(listener)
    except Exception as e:
        raise Exception(
            str(e)) from None
    else:
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
