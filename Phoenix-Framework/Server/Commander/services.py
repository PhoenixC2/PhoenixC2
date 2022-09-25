"""Starts the different services"""
import threading

from Commander import Commander
from Creator.listener import start_listener
from Database import ListenerModel, Session
from Utils.ui import log
from Utils.web import FlaskThread
from Web import create_web


def start_listeners(commander: Commander):
    """Start all listeners in the database"""
    # Get Listeners from Database
    listeners: list[ListenerModel] = Session.query(ListenerModel).all()
    # Start Listeners
    for listener in listeners:
        try:
            start_listener(listener, commander)
            log(f"Started listener {listener.name} ({listener.id})", "success")
        except Exception as error:
            log(str(error), "error")
            exit()
    Session.remove()

def start_web(address: str, port: int, ssl:bool, commander: Commander):
    """Start the web server"""
    web_server = create_web(commander)
    thread = FlaskThread(web_server, address, port, ssl, "WebServer")
    commander.web_server = thread
    commander.web_server.start()
    return web_server
