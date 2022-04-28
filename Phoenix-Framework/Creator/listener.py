from Utils import *
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
