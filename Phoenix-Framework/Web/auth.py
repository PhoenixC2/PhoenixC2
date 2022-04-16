from Utils import *


def auth_endpoints():
    auth = Blueprint("auth", __name__, url_prefix="/auth")
    return auth
