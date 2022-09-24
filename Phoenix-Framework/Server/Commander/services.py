"""Starts the different services"""
import threading

from Commander import Commander
from Creator.listener import start_listener
from Database import ListenerModel, db_session
from Utils.ui import log
from Web import create_web


def start_listeners(commander: Commander):
    """Start all listeners in the database"""
    # Get Listeners from Database
    listeners: list[ListenerModel] = db_session.query(ListenerModel).all()
    # Start Listeners
    for listener in listeners:
        try:
            start_listener(listener, commander)
            log(f"Started listener {listener.name} ({listener.id})", "success")
        except Exception as error:
            log(str(error), "error")
            exit()

def start_web(web_address: str, web_port: int, ssl:bool, commander: Commander):
    """Start the web server"""
    web_server = create_web(commander)
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
