from Utils import *
from Web.Endpoints.authorization import authorized, admin
from Creator.loader import *

loaders = Blueprint("loaders", __name__, url_prefix="/loaders")