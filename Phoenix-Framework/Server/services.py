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
        id = listener[0]
        name = listener[1]
        type = listener[2]
        type = type.replace("/", ".")
        type = "Listeners." + type
        config = json.loads(listener[3])
        # Get the Listener from the File
        server.all_listeners += 1
        listener = importlib.import_module(type).Listener(server, config, server.all_listeners)
        listener.start()
        server.add_listener(listener)
        log(f"Started {name} ({id})", "info")


def start_web(web_address, web_port, server : Server_Class):
    """Start the web server"""
    Web = create_web(server)
    try:
        threading.Thread(target=Web.run, kwargs={
            "host": web_address, "port": web_port}, name="WebServer").start()
    except:
        raise Exception("Could not start Web Server")
    else:
        return Web


