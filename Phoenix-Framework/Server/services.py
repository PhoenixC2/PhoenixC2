"""Starts the diffrent services"""
from Utils import curr, log, threading
from Web import create_web
from Creator.listener import start_listener
from Server.server_class import ServerClass


def start_listeners(server: ServerClass):
    """Start all listeners in the database"""
    # Get Listeners from Database
    curr.execute("SELECT * FROM Listeners")
    listeners = curr.fetchall()

    # Start Listeners
    for listener in listeners:
        try:
            start_listener(listener[0], server)
            log(f"Started Listener {listener[1]} ({listener[0]})", "success")
        except Exception as error:
            log(str(error), "error")


def start_web(web_address: str, web_port: int, ssl:bool, server: ServerClass):
    """Start the web server"""
    web_server = create_web(server)
    if ssl:
        threading.Thread(
            target=web_server.run,
            kwargs={
                "host": web_address,
                "port": web_port,
                "ssl_context": ("Data/ssl.pem", "Data/ssl.key"),
                "threaded": True},
            name="WebServer"
        ).start()
    else:
        threading.Thread(
            target=web_server.run,
            kwargs={
                "host": web_address,
                "port": web_port,
                "threaded": True},
            name="WebServer"
        ).start()
    return web_server
