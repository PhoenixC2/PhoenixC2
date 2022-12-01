"""The Web Server Class to interact with the Server using an API and a Web Interface"""
import json
import logging
import os
import random
import string

from flask import Flask, cli

from phoenix_framework.server.commander import Commander
from phoenix_framework.server.utils.config import load_config, save_config
from phoenix_framework.server.utils.web import get_messages
from phoenix_framework.server.web.endpoints import *
from phoenix_framework.server.web.endpoints.auth import get_current_user

# disable flask logging


def create_web(commander: Commander) -> Flask:
    web_server = Flask(__name__)
    if "2" not in os.getenv("PHOENIX_DEBUG", "") and "4" not in os.getenv(
        "PHOENIX_DEBUG", ""
    ):
        cli.show_server_banner = lambda *args: None
        logging.getLogger("werkzeug").disabled = True

    config = load_config()
    secret_key = config["web"]["secret_key"]
    if secret_key == "":
        secret_key = "".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(32)
        )
        config["web"]["secret_key"] = secret_key
        save_config(config)
    web_server.secret_key = secret_key

    @web_server.context_processor
    def inject_user():
        return dict(user=get_current_user())

    @web_server.context_processor
    def inject_messages():
        return dict(messages=get_messages())

    @web_server.context_processor
    def utility_processor():
        def to_json(data, *args, **kwargs):
            return json.dumps(data.to_dict(*args, **kwargs), default=str)

        return dict(to_json=to_json)

    web_server.register_blueprint(routes_bp(commander), url_prefix="/")
    web_server.register_blueprint(auth_bp, url_prefix="/auth")
    web_server.register_blueprint(users_bp, url_prefix="/users")
    web_server.register_blueprint(stagers_bp(commander), url_prefix="/stagers")
    web_server.register_blueprint(listeners_bp(commander), url_prefix="/listeners")
    web_server.register_blueprint(devices_bp(commander), url_prefix="/devices")
    web_server.register_blueprint(modules_bp, url_prefix="/modules")
    web_server.register_blueprint(loaders_bp, url_prefix="/loaders")
    web_server.register_blueprint(misc_bp, url_prefix="/misc")
    web_server.register_blueprint(tasks_bp(commander), url_prefix="/tasks")
    web_server.register_blueprint(logs_bp, url_prefix="/logs")
    return web_server
