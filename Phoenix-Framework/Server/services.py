from Utils import *
from Web import create_web
from Creator import start_listener
from Server.server_class import Server_Class


def start_listeners(server : Server_Class):
    # Get Listeners from Database
    curr.execute("SELECT * FROM Listeners")
    listeners = curr.fetchall()

    # Start Listeners
    for listener in listeners:
        try:
            start_listener(listener[0], server)
            log(f"Started Listener {listener[1]} ({listener[0]})", "success")
        except Exception as e:
            log(str(e), "error")



def start_web(web_address, web_port, ssl, server : Server_Class):
    """Start the web server"""
    Web = create_web(server)
    try:
        if ssl:
            threading.Thread(target=Web.run, kwargs={
            "host": web_address, "port": web_port, "ssl_context": ("Data/ssl.pem", "Data/ssl.key"), "threaded": True}, name="WebServer").start()
        else:
            threading.Thread(target=Web.run, kwargs={
            "host": web_address, "port": web_port, "threaded": True}, name="WebServer").start()
    except:
        raise Exception("Could not start Web Server")
    else:
        return Web


