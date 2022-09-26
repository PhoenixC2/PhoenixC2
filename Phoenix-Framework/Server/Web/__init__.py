"""The Web Server Class to interact with the Server using an API and a Web Interface"""
import logging
import os
import random
import string

from Commander import Commander
from flask import Flask, cli
from Web.Endpoints import *
from Web.Endpoints.authorization import get_current_user

# disable flask logging


def create_web(commander: Commander):
    web_server = Flask(__name__)
    if not os.getenv("PHOENIX_DEBUG", "") == "true":
        cli.show_server_banner = lambda *args: None
        logging.getLogger("werkzeug").disabled = True
    
    web_server.config["SECRET_KEY"] = "".join(
        random.choice(string.ascii_letters) for i in range(32))
    web_server.config["SECRET_KEY"] = "lol"
    print("Using session key lol")
    web_server.register_blueprint(routes_bp(commander), url_prefix="/")
    web_server.register_blueprint(auth_bp, url_prefix="/auth")
    web_server.register_blueprint(users_bp, url_prefix="/users")
    web_server.register_blueprint(stagers_bp(commander), url_prefix="/stagers")
    web_server.register_blueprint(
        listeners_bp(commander), url_prefix="/listeners")
    web_server.register_blueprint(devices_bp(commander), url_prefix="/devices")
    web_server.register_blueprint(modules_bp, url_prefix="/modules")
    web_server.register_blueprint(loaders_bp, url_prefix="/loaders")
    web_server.register_blueprint(misc_bp, url_prefix="/misc")
    web_server.register_blueprint(tasks_bp(commander), url_prefix="/tasks")
    web_server.register_blueprint(logs_bp, url_prefix="/logs")
    return web_server
