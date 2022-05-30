from Utils import *
misc = Blueprint("mics", __name__, url_prefix="/misc")

@misc.route("/version")
def get_phoenix():
    return jsonify({"version": version})