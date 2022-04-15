from Utils import *
from Web import *
from Server.server_class import *


def start_listeners(server : Server_Class, curr):
    """Start all Listeners by querying the database
    and initializing the corresponding listener class"""
    # Get Listeners from Database
    curr.execute("SELECT * FROM Listeners")
    listeners = curr.fetchall()
    # Start Listeners
    for listener in listeners:
        type = listener[2]
        type = type.replace("/", ".")
        type = "Listeners." + type
        config = json.loads(listener[3])
        # Get the Listener from the File
        listener = importlib.import_module(type).Listener(server, config, len(server.listeners) + 1)
        listener.start()
        server.add_listener(listener)


def start_web(web_address, web_port):
    """Start the web server"""
    Web = create_web()
    try:
        threading.Thread(target=Web.run, kwargs={
            "host": web_address, "port": web_port}, name="WebServer").start()
    except:
        raise Exception("Could not start Web Server")
    else:
        return Web


