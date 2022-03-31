from globals import *
from Web.api import api_endpoints
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

def create_web(Handler):
    Api = Flask(__name__)
    Api.config["SECRET_KEY"] = "".join(random.choice(string.ascii_letters) for i in range(32))
    Api.register_blueprint(api_endpoints(Handler), url_prefix="/api")
    Api.register_blueprint(auth_endpoints(), url_prefix="/auth")
    Api.register_blueprint(routes_endpoints(), url_prefix="/")
    return Api