from flask import Blueprint

from phoenix.server.utils.web import authorized

loaders_bp = Blueprint("loaders", __name__, url_prefix="/loaders")
