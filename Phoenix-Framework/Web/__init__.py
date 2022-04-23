"""The Web Server Class to interact with the Server using an API and a Web Interface"""
from Utils import *
from Web.devices import devices_enpoints
from Web.auth import auth
from Web.routes import routes
import random
import string
import logging

# disable flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass

def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass

click.echo = echo
click.secho = secho

def create_web(server):
    Webserver = Flask(__name__)
    Webserver.config["SECRET_KEY"] = "".join(random.choice(string.ascii_letters) for i in range(32))
    Webserver.register_blueprint(devices_enpoints(server), url_prefix="/devices")
    Webserver.register_blueprint(auth, url_prefix="/auth")
    Webserver.register_blueprint(routes, url_prefix="/")
    return Webserver