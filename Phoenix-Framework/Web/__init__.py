"""The Web Server Class to interact with the Server using an API and a Web Interface"""
from Utils import *
from Web.devices import devices_enpoints
from Web.auth import auth_endpoints
from Web.routes import routes_endpoints
import random
import string

# disable flask logging
def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass
def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass
click.echo = echo
click.secho = secho

def create_web(server):
    Api = Flask(__name__)
    Api.config["SECRET_KEY"] = "".join(random.choice(string.ascii_letters) for i in range(32))
    Api.register_blueprint(devices_enpoints(server), url_prefix="/devices")
    Api.register_blueprint(auth_endpoints(), url_prefix="/auth")
    Api.register_blueprint(routes_endpoints(), url_prefix="/")
    return Api