from flask import Blueprint, jsonify, request
from Utils.misc import version
from Creator.options import *
misc_bp = Blueprint("misc", __name__, url_prefix="/misc")

@misc_bp.route("/version", methods=["GET"])
def get_phoenix():
    return jsonify({"version": version})

@misc_bp.route("/available", methods=["GET"])
def available():
    options = {
        "listeners": AVAILABLE_LISTENERS,
        "encodings": AVAILABLE_ENCODINGS,
        "stagers": AVAILABLE_STAGERS,
        "loaders": AVAILABLE_LOADERS,
        "formats": AVAILABLE_FORMATS
    }
    return jsonify(options)