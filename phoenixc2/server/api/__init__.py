"""The Web Server Class to interact with the Server using an API and a Web Interface"""
import logging
import os
import secrets
from flask import Blueprint, Flask, abort, cli, request

from phoenixc2.server.commander.commander import Commander
from phoenixc2.server.utils.config import load_config, save_config
from phoenixc2.server.utils.ui import log
from phoenixc2.server.api.endpoints.auth import auth_bp
from phoenixc2.server.api.endpoints.credentials import credentials_bp
from phoenixc2.server.api.endpoints.dashboard import dashboard_bp
from phoenixc2.server.api.endpoints.devices import devices_bp
from phoenixc2.server.api.endpoints.listeners import listeners_bp
from phoenixc2.server.api.endpoints.loaders import loaders_bp
from phoenixc2.server.api.endpoints.logs import logs_bp
from phoenixc2.server.api.endpoints.misc import misc_bp
from phoenixc2.server.api.endpoints.modules import modules_bp
from phoenixc2.server.api.endpoints.operations import operations_bp
from phoenixc2.server.api.endpoints.stagers import stagers_bp
from phoenixc2.server.api.endpoints.tasks import tasks_bp
from phoenixc2.server.api.endpoints.users import users_bp
from phoenixc2.server.api.endpoints.bypasses import bypasses_bp

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
    "bypasses": bypasses_bp,
}


def create_api(commander: Commander) -> Flask:
    web_server = Flask(__name__)
    web_server.jinja_options["autoescape"] = lambda _: True
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
        secret_key = secrets.token_urlsafe(32)
        config["web"]["secret_key"] = secret_key
        save_config(config)
    elif len(secret_key) < 30:
        log("The session secret key is short. Consider changing it.", "critical")

    web_server.secret_key = secret_key

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
            endpoints[endpoint], url_prefix="/api/" + endpoints[endpoint].url_prefix
        )
    log(f"Registered {len(endpoints)} endpoints", "info")
    return web_server
