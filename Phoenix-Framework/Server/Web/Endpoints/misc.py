from Creator.available import *
from flask import Blueprint, jsonify
from Utils.misc import get_network_interfaces, version
from Utils.web import authorized

misc_bp = Blueprint("misc", __name__, url_prefix="/misc")

@misc_bp.route("/version", methods=["GET"])
def get_phoenix():
    return jsonify({"version": version})


@misc_bp.route("/available", methods=["GET"])
@authorized
def get_available():
    options = {
        "listeners": AVAILABLE_LISTENERS,
        "encodings": AVAILABLE_ENCODINGS,
        "stagers": AVAILABLE_STAGERS,
        "loaders": AVAILABLE_LOADERS,
        "formats": AVAILABLE_FORMATS
    }
    return jsonify(options)

@misc_bp.route("/interfaces", methods=["GET"])
@authorized
def get_interfaces():
    return get_network_interfaces()