from Utils.libraries import Blueprint, jsonify
from Utils.misc import version
misc_bp = Blueprint("mics", __name__, url_prefix="/misc")

@misc_bp.route("/version")
def get_phoenix():
    return jsonify({"version": version})