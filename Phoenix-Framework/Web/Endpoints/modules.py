from flask import Blueprint
from Utils.web import authorized

modules_bp = Blueprint("modules", __name__, url_prefix="/modules")