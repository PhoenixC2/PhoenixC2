"""The Web Server Class to interact with the Server using an API and a Web Interface"""
import json
import logging
import os
import random
import string

from flask import Flask, abort, cli, request

from phoenixc2.server.commander import Commander
from phoenixc2.server.database import (LogEntryModel, OperationModel, Session,
                                       UserModel)
from phoenixc2.server.utils.config import load_config, save_config
from phoenixc2.server.web.endpoints import *
from phoenixc2.server.utils.misc import format_datetime

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
        # check if the secret key is set in the config
        # if not, generate a new one and save it
        secret_key = "".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(32)
        )
        config["web"]["secret_key"] = secret_key
        save_config(config)

    web_server.secret_key = secret_key

    # context processors for the templates
    @web_server.context_processor
    def inject_user():
        return dict(user=UserModel.get_current_user())

    @web_server.context_processor
    def inject_messages():
        return dict(
            messages=[
                log
                for log in Session.query(LogEntryModel).all()
                if UserModel.get_current_user() in log.unseen_users
            ]
        )

    @web_server.context_processor
    def inject_operation():
        return dict(current_operation=OperationModel.get_current_operation())

    @web_server.context_processor
    def inject_to_dict():
        # function which converts a database element to a json string to be used in javascript
        def to_json(data, *args, **kwargs):
            return json.dumps(data.to_dict(*args, **kwargs), default=str)

        return dict(to_json=to_json)

    @web_server.context_processor
    def inject_format_datetime():
        return dict(format_datetime=format_datetime)

    @web_server.before_request
    def before_request():
        # check if the show cookie is enabled and if the request has the cookie
        # if not show 403

        if (
            config["web"]["show_cookie"]
            and request.cookies.get(config["web"]["show_cookie_name"])
            != config["web"]["show_cookie_value"]
        ):
            return abort(403)

    web_server.register_blueprint(routes_bp(commander), url_prefix="/")
    web_server.register_blueprint(stagers_bp(commander), url_prefix="/stagers")
    web_server.register_blueprint(listeners_bp(commander), url_prefix="/listeners")
    web_server.register_blueprint(devices_bp(commander), url_prefix="/devices")
    web_server.register_blueprint(modules_bp(commander), url_prefix="/modules")
    web_server.register_blueprint(auth_bp, url_prefix="/auth")
    web_server.register_blueprint(users_bp, url_prefix="/users")
    web_server.register_blueprint(loaders_bp, url_prefix="/loaders")
    web_server.register_blueprint(misc_bp, url_prefix="/misc")
    web_server.register_blueprint(tasks_bp(commander), url_prefix="/tasks")
    web_server.register_blueprint(logs_bp, url_prefix="/logs")
    web_server.register_blueprint(operations_bp, url_prefix="/operations")
    return web_server
