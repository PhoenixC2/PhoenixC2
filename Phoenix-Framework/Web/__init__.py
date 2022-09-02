"""The Web Server Class to interact with the Server using an API and a Web Interface"""
import random
import string
import logging
from flask import Flask, cli, session, flash, redirect
from Web.Endpoints import *
from Web.Endpoints.authorization import get_current_user
from Server.server_class import ServerClass

# disable flask logging



def create_web(server: ServerClass, debug:bool):
    web_server = Flask(__name__)
    if not debug:
        cli.show_server_banner = lambda *args: None
        logging.getLogger("werkzeug").disabled = True
    @web_server.before_request
    def before_request():
        if session.get("id"):
            user = get_current_user()
            if user.disabled:
                flash("Your account got disabled!", "error")
                session.clear()
                return redirect("/")

    web_server.config["SECRET_KEY"] = "".join(
        random.choice(string.ascii_letters) for i in range(32))
    web_server.register_blueprint(routes_bp, url_prefix="/")
    web_server.register_blueprint(auth_bp, url_prefix="/auth")
    web_server.register_blueprint(users_bp, url_prefix="/users")
    web_server.register_blueprint(stagers_bp, url_prefix="/stagers")
    web_server.register_blueprint(
        listeners_bp(server), url_prefix="/listeners")
    web_server.register_blueprint(devices_bp(server), url_prefix="/devices")
    web_server.register_blueprint(modules_bp, url_prefix="/modules")
    web_server.register_blueprint(loaders_bp, url_prefix="/loaders")
    return web_server
