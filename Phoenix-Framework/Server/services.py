from Utils import *
from Web import *


def start_listeners(server, curr):
    # Get Listeners from Database
    curr.execute("SELECT * FROM Listeners")
    listeners = curr.fetchall()
    # Start Listeners
    for listener in listeners:
        type = listener[2]
        config = listener[3]
        listener = importlib.import_module(type).Listener(server, config)
        listener.start()
        server.listeners.append(listener)


def start_web(web_address, web_port):
    Web = create_web()
    try:
        threading.Thread(target=Web.run, kwargs={
            "host": web_address, "port": web_port}, name="WebServer").start()
    except:
        raise Exception("Could not start Web Server")
    else:
        return Web


def check_db():
    conn = connect("Data/db.sqlite3")
    curr = conn.cursor()
    try:
        curr.execute("SELECT * FROM Devices")
        curr.fetchall()
    except:
        raise Exception("Database isnt configured.")
    return conn, curr
