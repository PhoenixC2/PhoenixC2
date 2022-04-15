from Utils import *

def create_listener(listener, address, port, listener_type):
    """
    Create a payload 
    """
    # Check if Listener exists
    try:
        with open("Listeners/" + payload + ".py", "r") as f:
            payload = f.read()
    except:
        raise Exception("Could not find the Listener")