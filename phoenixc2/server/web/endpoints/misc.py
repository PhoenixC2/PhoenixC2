import os

from flask import Blueprint, jsonify, send_from_directory

import phoenixc2
import phoenixc2.server as avl
from phoenixc2.server.database import UserModel
from phoenixc2.server.utils.misc import get_network_interfaces
from phoenixc2.server.utils.resources import get_resource
from phoenixc2.server.utils.web import generate_response

misc_bp = Blueprint("misc", __name__, url_prefix="/misc")


@misc_bp.route("/version", methods=["GET"])
def get_phoenix():
    return jsonify({"version": phoenixc2.__version__})


@misc_bp.route("/available", methods=["GET"])
@UserModel.authenticated
def get_available():
    options = {
        "kits": avl.INSTALLED_KITS,
        "encodings": avl.INSTALLED_ENCODINGS,
        "loaders": avl.INSTALLED_LOADERS,
    }
    return jsonify(options)


@misc_bp.route("/interfaces", methods=["GET"])
@UserModel.authenticated
def get_interfaces():
    return get_network_interfaces()


@misc_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "success"})


@misc_bp.route("/downloads/<string:file_name>", methods=["GET"])
@UserModel.authenticated
def get_downloads(file_name: str):
    if file_name is None:
        return generate_response("danger", "File name is missing.", "devices", 400)

    return send_from_directory(
        str(get_resource("data/downloads", skip_file_check=True)),
        file_name,
        as_attachment=True,
    )


@misc_bp.route("/uploads/clear", methods=["POST"])
@UserModel.admin_required
def post_clear_uploads():
    uploads = get_resource("data/uploads", skip_file_check=True)
    for file in uploads.iterdir():
        os.remove(file)
    return generate_response("success", "Uploads cleared.", "devices")


@misc_bp.route("/downloads/clear", methods=["POST"])
@UserModel.admin_required
def post_clear_downloads():
    downloads = get_resource("data/downloads", skip_file_check=True)
    for file in downloads.iterdir():
        os.remove(file)
    return generate_response("success", "Downloads cleared.", "devices")
