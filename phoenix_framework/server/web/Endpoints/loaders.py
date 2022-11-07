from flask import Blueprint
from phoenix_framework.server.utils.web import authorized

# from Creator.loader import *

loaders_bp = Blueprint("loaders", __name__, url_prefix="/loaders")
