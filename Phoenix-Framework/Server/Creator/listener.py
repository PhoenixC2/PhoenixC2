"""Create Listeners"""
import time
import importlib
from typing import Optional
from Database import db_session, ListenerModel
from Commander.commander import Commander
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
                             listener_type=listener_type,
                             address=address,
                             port=port,
                             ssl=ssl,
                             connection_limit=connection_limit)
    db_session.add(listener)
    db_session.commit()
    return f"Listener {name} created"


def start_listener(listener_db: ListenerModel, server: Commander) -> Optional[str]:
    """
    Start a listener

    :param listener_id: The ID of the listener
    :param server: The main server
    :return: Status

    """

    # Check if Listener is already active
    try:
        server.get_active_listener(listener_db.id)
    except:
        pass
    else:
        raise Exception("Listener is already active!") from None
    # Get the Listener from the File
    listener: BaseListener = importlib.import_module("Listeners." + listener_db.listener_type.replace("/", ".")).Listener(
        server, listener_db)

    # Start Listener
    try:
        listener.start()
        server.add_active_listener(listener)
    except Exception as e:
        raise Exception(
            str(e)) from None
    else:
        return f"Started Listener with ID {listener_db.id}"


def stop_listener(listener_db: ListenerModel, server: Commander) -> None:
    """
    Stop a listener

    :param listener_id: The ID of the listener
    :param server: The main server

    """
    listener = server.get_active_listener(listener_db.id)
    listener.stop()
    server.remove_listener(listener_db.id)

def restart_listener(listener_db: ListenerModel, server: Commander) -> None:
    """
    Restart a listener
    
    :param listener_id: The ID of the listener
    :param server: The main server
    """
    stop_listener(listener_db, server)
    time.sleep(5)
    start_listener(listener_db, server)
