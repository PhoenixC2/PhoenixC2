"""Starts the different services"""
import threading

from commander import Commander
from creator.listener import start_listener
from database import ListenerModel, Session
from utils.ui import log
from utils.web import FlaskThread
from web import create_web


def start_listeners(commander: Commander):
    """Start all listeners in the database"""
    # Get Listeners from Database
    listeners: list[ListenerModel] = Session.query(ListenerModel).filter_by(enabled=True).all()
    # Start Listeners
    for listener in listeners:
        try:
            # Start Listener
            start_listener(listener, commander)
            log(f"Started listener {listener.name} ({listener.id})", "success")
        except Exception as error:
            log(str(error), "danger")
            exit()
    Session.remove()

def start_web(address: str, port: int, ssl:bool, commander: Commander):
    """Start the web server"""
    # Create Web App
    web_server = create_web(commander)
    # Create Thread
    commander.web_server = FlaskThread(web_server, address, port, ssl, "WebServer")
    # Start Thread
    commander.web_server.start()
    return web_server
