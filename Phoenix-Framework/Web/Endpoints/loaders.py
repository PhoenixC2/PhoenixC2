from Utils import *
from Web.Endpoints.authorization import authorized, admin

loaders = Blueprint("loaders", __name__, url_prefix="/loaders")