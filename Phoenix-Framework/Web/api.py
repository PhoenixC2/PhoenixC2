from Utils.ui import *


def api_enpoints(Handler):
    api = Blueprint("api", __name__, url_prefix="/api")

    return api