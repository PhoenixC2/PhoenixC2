"""Create Listeners"""
from typing import Optional
from Utils.libraries import json, importlib
from Database import session, ListenerModel
from Server.server_class import ServerClass
from Listeners.base import Base_Listener
from .options import listeners as available_listeners


def create_listener(listener_type: str = None,
                    name: str = None,
                    address: str = None,
                    port: int = None,
                    ssl: bool = False) -> str:
    """
    Create a Listener

    :param type: The Type of Listener
    :param name: The Name of the Listener
    :param address: The Address of the Listener
    :param port: The Port of the Listener
    :return: The Listener as a string

    """
    # Check if Listener exists
    if session.query(ListenerModel).filter_by(name=name).first:
        raise Exception(f"Listener {name} already exists")

    # Check if type is valid
    if listener_type[0] == "/":
        listener_type = listener_type[1:]

    if listener_type not in available_listeners:
        raise Exception(f"Listener {listener_type} is not available.")
    try:
        open("Listeners/" + listener_type + ".py", "r").close()
    except:
        raise Exception(f"Listener {listener_type} does not exist") from None

    # Create Config
    config = {
        "address": address,
        "port": port,
        "ssl": ssl
    }

    # Save Listener
    listener = ListenerModel(name=name,
                             listener_type=listener_type,
                             config=config)
    session.add(listener)
    session.commit()
    return f"Listener {name} created"


def start_listener(listener_id: int, server: ServerClass) -> Optional[str]:
    """
    Start a Listener

    :param listener_id: The ID of the Listener
    :return: Status

    """

    # Check if Listener exists
    listener_db: ListenerModel = session.query(
        ListenerModel).filter_by(listener_id=listener_id).first()
    if not listener_db:
        raise Exception(f"Listener with ID {listener_id} does not exist")

    # Check if Listener is already active
    try:
        server.get_active_listener(listener_db.listener_id)
    except:
        raise Exception("Listener is already active!") from None
    # Get the Listener from the File
    listener: Base_Listener = importlib.import_module(listener_db.listener_type).Listener(
        server, listener_db.config, listener_db)

    # Start Listener
    try:
        listener.start()
        server.add_active_listener(listener)
    except Exception as e:
        raise Exception(
            f"Failed to start Listener {listener_db.name}") from None
    else:
        return f"Started Listener with ID {listener_id}"


def stop_listener(listener_id: int, server: ServerClass) -> None:
    """
    Stop a Listener

    :param id: The ID of the Listener
    :return: Status

    """
    listener = server.get_active_listener(listener_id)
    listener.stop()
    server.remove_listener(listener_id)
