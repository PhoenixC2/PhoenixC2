import phoenix_framework.server.creator.available as avl
from flask import Blueprint, jsonify
from phoenix_framework.server.utils.misc import get_network_interfaces, version
from phoenix_framework.server.utils.web import authorized

misc_bp = Blueprint("misc", __name__, url_prefix="/misc")

@misc_bp.route("/version", methods=["GET"])
def get_phoenix():
    return jsonify({"version": version})


@misc_bp.route("/available", methods=["GET"])
@authorized
def get_available():
    options = {
        "kits": avl.AVAILABLE_KITS,
        "encodings": avl.AVAILABLE_ENCODINGS,
        "payloads": avl.AVAILABLE_PAYLOADS,
        "loaders": avl.AVAILABLE_LOADERS,
    }
    return jsonify(options)

@misc_bp.route("/interfaces", methods=["GET"])
@authorized
def get_interfaces():
    return get_network_interfaces()