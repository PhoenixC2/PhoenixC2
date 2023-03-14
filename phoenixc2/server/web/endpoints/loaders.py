from flask import Blueprint, render_template, request
from phoenixc2.server.database import UserModel

loaders_bp = Blueprint("loaders", __name__, url_prefix="/loaders")


@loaders_bp.route("/")
@loaders_bp.route("/<string:loader_name>")
@UserModel.authenticated
def get_loader(loader_name: str = None):
    use_json = request.args.get("json", "").lower() == "true"

    if use_json:
        return {"status": "error", "message": "Not implemented."}, 501

    return render_template("loaders.j2")
