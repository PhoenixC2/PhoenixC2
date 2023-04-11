from flask import Blueprint
from phoenixc2.server.database import UserModel

loaders_bp = Blueprint("loaders", __name__, url_prefix="/loaders")


@loaders_bp.route("/")
@loaders_bp.route("/<string:loader_name>")
@UserModel.authenticated
def get_loader(loader_name: str = None):
    return {"status": "error", "message": "Not implemented yet."}, 501
