"""Starts the different services"""
import threading

from phoenix_framework.server.database import ListenerModel, Session
from phoenix_framework.server.utils.ui import log
from phoenix_framework.server.utils.web import FlaskThread
from phoenix_framework.server.web import create_web

from .commander import Commander


def start_listeners(commander: Commander):
    """Start all listeners in the database"""
    # Get Listeners from Database
    listeners: list[ListenerModel] = (
        Session.query(ListenerModel).filter_by(enabled=True).all()
    )
    # Start Listeners
    for listener in listeners:
        try:
            # Start Listener
            status = listener.start(commander)
        except Exception as error:
            log(str(error), "danger")
            exit()
        else:
            log(status, "success")
    Session.remove()


def start_web(address: str, port: int, ssl: bool, commander: Commander):
    """Start the web server"""
    # Create Web App
    web_server = create_web(commander)
    # Create Thread
    commander.web_server = FlaskThread(web_server, address, port, ssl, "WebServer")
    # Start Thread
    commander.web_server.start()
    return web_server
