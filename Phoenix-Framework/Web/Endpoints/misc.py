from Utils.libraries import Blueprint, jsonify
from Utils.misc import version
misc = Blueprint("mics", __name__, url_prefix="/misc")

@misc.route("/version")
def get_phoenix():
    return jsonify({"version": version})