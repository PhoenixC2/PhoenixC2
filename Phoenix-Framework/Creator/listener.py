from Utils import *
from Server import Server_Class
def create_listener(listener_type : str = None, name : str = None, address : str = None, port : int = None, ssl : bool = False) -> str:
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
    try:
        open("Listeners/" + listener_type + ".py", "r").close()
    except:
        raise Exception(f"Listener {listener_type} does not exist")
    # Create Config
    config = {
        "address": address,
        "port": port,
        "ssl": ssl
    }
    # Save Listener
    curr.execute("INSERT INTO Listeners (Name, Type, Config) VALUES (?, ?, ?)", (name, listener_type, json.dumps(config)))
    conn.commit()
    return f"Listener {name} created"

def start_listener(id: int, server : Server_Class) -> None:
    """
    Start a Listener

    :param id: The ID of the Listener
    :return: Status

    """

    # Check if Listener exists
    curr.execute("SELECT * FROM Listeners WHERE ID = ?", (id,))
    listener = curr.fetchone()
    if not listener:
        raise Exception(f"Listener with ID {id} does not exist")
    
    # Load Listener
    id = listener[0]
    name = listener[1]
    type = listener[2]
    type = type.replace("/", ".")
    type = "Listeners." + type
    config = json.loads(listener[3])
    
    # Get the Listener from the File
    listener = importlib.import_module(type).Listener(server, config, server.active_listeners_count + 1)

    # Start Listener
    try:

        listener.start()
        server.add_listener(listener)
        server.active_listeners_count += 1
    except:
        log(f"Failed to start {name} ({server.active_devices_count})", "error")
        raise Exception(f"Failed to start Listener [{name}]")
    else:
        log(f"Started {name} ({server.active_listeners_count})", "info")
        return f"Started Listener with ID {id}"

def stop_listener(id: int, server : Server_Class) -> None:
    """
    Stop a Listener

    :param id: The ID of the Listener
    :return: Status

    """

    # Check if Listener exists
    curr.execute("SELECT * FROM Listeners WHERE ID = ?", (id,))
    listener = curr.fetchone()
    if not listener:
        raise Exception(f"Listener with ID {id} does not exist")
    name = listener[1]

    listener.stop()
    try:
        server.remove_listener(id)
        server.active_listeners_count -= 1
    except:
        log(f"Failed to stop {name} ({server.active_devices_count})", "error")
        return f"Failed to stop Listener with ID {id}"
    else:
        log(f"Stopped {name} ({server.active_devices_count})", "info")
        return f"Stopped Listener with ID {id}"