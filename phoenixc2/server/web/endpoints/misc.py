from flask import Blueprint, send_from_directory

from phoenixc2.server.database import UserModel
from phoenixc2.server.utils.misc import get_network_interfaces
from phoenixc2.server.utils.resources import get_resource
from phoenixc2.server.utils.misc import Status

misc_bp = Blueprint("misc", __name__, url_prefix="/misc")


@misc_bp.route("/interfaces", methods=["GET"])
@UserModel.authenticated
def get_interfaces():
    return get_network_interfaces()


@misc_bp.route("/downloads/<string:file_name>", methods=["GET"])
@UserModel.authenticated
def get_downloads(file_name: str):
    if file_name is None:
        return {"status": Status.ERROR, "message": "No file specified."}

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
        file.unlink()
    return {"status": Status.SUCCESS, "message": "Uploads cleared."}


@misc_bp.route("/downloads/clear", methods=["POST"])
@UserModel.admin_required
def post_clear_downloads():
    downloads = get_resource("data/downloads", skip_file_check=True)
    for file in downloads.iterdir():
        file.unlink()
    return {"status": Status.SUCCESS, "message": "Downloads cleared."}
