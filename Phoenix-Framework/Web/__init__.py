"""The Web Server Class to interact with the Server using an API and a Web Interface"""
from Utils.libraries import os, Flask
from Web.Endpoints import *
import random
import string
import logging

# disable flask logging
os.environ["WERKZEUG_RUN_MAIN"] = "true"
log = logging.getLogger('werkzeug')
log.disabled = True


os.environ["WERKZEUG_RUN_MAIN"] = "true"

def create_web(server):
    Webserver = Flask(__name__)
    Webserver.logger.disabled = True
    Webserver.config["SECRET_KEY"] = "".join(random.choice(string.ascii_letters) for i in range(32))
    Webserver.register_blueprint(devices_enpoints(server), url_prefix="/devices")
    Webserver.register_blueprint(auth, url_prefix="/auth")
    Webserver.register_blueprint(routes, url_prefix="/")
    Webserver.register_blueprint(stagers, url_prefix="/stagers")
    Webserver.register_blueprint(listeners_endpoints(server), url_prefix="/listeners")
    Webserver.register_blueprint(modules, url_prefix="/modules")
    Webserver.register_blueprint(loaders, url_prefix="/loaders")
    return Webserver