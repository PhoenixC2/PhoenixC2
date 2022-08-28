from flask import Blueprint
from Web.Endpoints.authorization import authorized, admin
#from Creator.loader import *

loaders_bp = Blueprint("loaders", __name__, url_prefix="/loaders")