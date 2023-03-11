"""The Web Server Class to interact with the Server using an API and a Web Interface"""
import json
import logging
import os
import random
import string

from flask import Flask, abort, cli, request, Blueprint, render_template_string
from phoenixc2.server.commander import Commander
from phoenixc2.server.database import OperationModel, UserModel
from phoenixc2.server.utils.config import load_config, save_config
from phoenixc2.server.web.endpoints.auth import auth_bp
from phoenixc2.server.web.endpoints.devices import devices_bp
from phoenixc2.server.web.endpoints.listeners import listeners_bp
from phoenixc2.server.web.endpoints.operations import operations_bp
from phoenixc2.server.web.endpoints.users import users_bp
from phoenixc2.server.web.endpoints.dashboard import dashboard_bp
from phoenixc2.server.web.endpoints.tasks import tasks_bp
from phoenixc2.server.web.endpoints.stagers import stagers_bp
from phoenixc2.server.web.endpoints.modules import modules_bp
from phoenixc2.server.web.endpoints.loaders import loaders_bp
from phoenixc2.server.web.endpoints.misc import misc_bp
from phoenixc2.server.web.endpoints.logs import logs_bp
from phoenixc2.server.web.endpoints.credentials import credentials_bp
from phoenixc2.server.utils.ui import log

from phoenixc2.server.utils.misc import format_datetime

endpoints: dict[str, Blueprint] = {
    "routes": dashboard_bp,
    "stagers": stagers_bp,
    "listeners": listeners_bp,
    "devices": devices_bp,
    "modules": modules_bp,
    "auth": auth_bp,
    "users": users_bp,
    "loaders": loaders_bp,
    "misc": misc_bp,
    "tasks": tasks_bp,
    "logs": logs_bp,
    "operations": operations_bp,
    "credentials": credentials_bp,
}


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
            random.choice(string.ascii_letters + string.digits) for _ in range(50)
        )
        config["web"]["secret_key"] = secret_key
        save_config(config)
    elif len(secret_key) < 30:
        log("The session secret key is short. Consider changing it.", "critical")

    web_server.secret_key = secret_key

    # context processors for the templates
    @web_server.context_processor
    def inject_user():
        return dict(user=UserModel.get_current_user())

    @web_server.context_processor
    def inject_operation():
        return dict(current_operation=OperationModel.get_current_operation())

    @web_server.context_processor
    def inject_commander():
        return dict(commander=commander)

    @web_server.context_processor
    def inject_to_dict():
        # converts a database element to a json string to be used in javascript
        def to_json(data, *args, **kwargs):
            return json.dumps(data.to_dict(*args, **kwargs), default=str)

        return dict(to_json=to_json)

    @web_server.context_processor
    def inject_format_datetime():
        return dict(format_datetime=format_datetime)

    @web_server.context_processor
    def inject_plugins():
        return dict(plugins=commander.injection_plugins)

    @web_server.context_processor
    def inject_render_template_string():
        # used to render plugins
        return dict(render_template_string=render_template_string)

    @web_server.context_processor
    def inject_icons():
        return dict(
            icons={
                "dashboard": "dashboard",
                "operations": "public",
                "devices": "dns",
                "listeners": "earbuds",
                "stagers": "code",
                "loaders": "download",
                "modules": "extension",
                "users": "group",
                "credentials": "vpn_key",
                "logs": "event_note",
            }
        )
    
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

    # register the blueprints
    for endpoint in endpoints:
        # check if endpoint is a function
        if callable(endpoints[endpoint]):
            endpoints[endpoint] = endpoints[endpoint](commander)
        web_server.register_blueprint(
            endpoints[endpoint], url_prefix=endpoints[endpoint].url_prefix
        )
    return web_server
