from Utils import *
from Web.Endpoints.authorization import authorized, admin

modules = Blueprint("modules", __name__, url_prefix="/modules")