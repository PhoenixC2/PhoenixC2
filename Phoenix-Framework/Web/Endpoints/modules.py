from Utils.libraries import Blueprint
from Web.Endpoints.authorization import authorized, admin

modules_bp = Blueprint("modules", __name__, url_prefix="/modules")