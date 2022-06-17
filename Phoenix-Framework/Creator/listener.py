"""Create Listeners"""
from Utils import (
    curr,
    conn,
    json,
    importlib)


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
    curr.execute("SELECT * FROM Listeners WHERE Name = ?", (name,))
    listener = curr.fetchone()
    if listener:
        raise Exception(f"Listener {name} already exists")
    # Check if type is valid
    if listener_type[0] == "/":
        listener_type = listener_type[1:]
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
    curr.execute("INSERT INTO Listeners (Name, Type, Config) VALUES (?, ?, ?)",
                 (name, listener_type, json.dumps(config)))
    conn.commit()
    return f"Listener {name} created"


def start_listener(listener_id: int, server) -> None:
    """
    Start a Listener

    :param id: The ID of the Listener
    :return: Status

    """

    # Check if Listener exists
    curr.execute("SELECT * FROM Listeners WHERE ID = ?", (listener_id,))
    listener = curr.fetchone()
    if not listener:
        raise Exception(f"Listener with ID {listener_id} does not exist")

    # Check if Listener is already active

    # Load Listener
    name = listener[1]
    listener_type = listener[2]
    listener_type = listener_type.replace("/", ".")
    listener_type = "Listeners." + listener_type
    config = json.loads(listener[3])

    # Get the Listener from the File
    listener = importlib.import_module(listener_type).Listener(
        server, config, listener_id)

    # Start Listener
    try:
        listener.start()
        server.add_listener(listener)
    except:
        raise Exception(f"Failed to start Listener {name}") from None
    else:
        return f"Started Listener with ID {listener_id}"


def stop_listener(listener_id: int, server) -> None:
    """
    Stop a Listener

    :param id: The ID of the Listener
    :return: Status

    """
    listener = server.get_listener(listener_id)
    listener.stop()
    server.remove_listener(listener_id)
