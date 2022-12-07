import os

from flask import Blueprint, jsonify, send_from_directory

import phoenix_framework.server as avl
from phoenix_framework.server.utils.misc import get_network_interfaces, version
from phoenix_framework.server.utils.resources import get_resource
from phoenix_framework.server.utils.web import admin, authorized, generate_response
from phoenix_framework.server.modules import get_all_module_paths

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


@misc_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})

@misc_bp.route("/modules", methods=["GET"])
def get_modules():
    return jsonify(get_all_module_paths())
@misc_bp.route("/downloads/<string:file_name>", methods=["GET"])
@authorized
def get_downloads(file_name: str):
    if file_name is None:
        return generate_response("danger", "File name is missing.", "devices", 400)

    return send_from_directory(
        str(get_resource("data/downloads", skip_file_check=True)),
        file_name,
        as_attachment=True,
    )


@misc_bp.route("/downloads/clear", methods=["POST"])
@admin
def post_clear_downloads():
    downloads = get_resource("data/downloads", skip_file_check=True)
    for file in downloads.iterdir():
        os.remove(file)
    return generate_response("success", "Downloads cleared.", "devices")


@misc_bp.route("/uploads/clear", methods=["POST"])
@admin
def post_clear_uploads():
    uploads = get_resource("data/uploads", skip_file_check=True)
    for file in uploads.iterdir():
        os.remove(file)
    return generate_response("success", "Uploads cleared.", "devices")
