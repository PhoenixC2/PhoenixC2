"""Starts the different services"""
import os

from phoenixc2.server.database import ListenerModel, Session
from phoenixc2.server.plugins import get_plugin
from phoenixc2.server.utils.config import load_config
from phoenixc2.server.utils.ui import log
from phoenixc2.server.utils.web import FlaskThread
from phoenixc2.server.web import create_web

from .commander import Commander


def start_listeners(commander: Commander):
    """Start all listeners in the database"""
    # Get Listeners from Database
    listeners: list[ListenerModel] = (
        Session.query(ListenerModel).filter_by(enabled=True).all()
    )
    # Start Listeners
    listeners_started = 0
    for listener in listeners:
        try:
            # Start Listener
            status = listener.start(commander)
        except Exception as error:
            log(str(error), "danger")
            exit()
        else:
            log(status, "success")
            listeners_started += 1
    log(f"{listeners_started} listener{'s' if listeners_started != 1 else ''} started.", "success")
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


def load_plugins(commander: Commander):
    """Load all plugins which are specified in the config"""
    plugins = load_config()["plugins"]
    for plugin in plugins.keys():
        plugin_config = plugins[plugin]
        if plugin_config["enabled"]:
            try:
                commander.load_plugin(get_plugin(plugin), plugin_config)
            except Exception as error:
                log(str(error), "danger")
                os._exit(1)
            else:
                log(f"Plugin '{plugin}' loaded.", "success")

    log(f"Loaded {len(plugins.keys())} plugin{'s' if len(plugins.keys()) != 1 else ''}.", "success")
