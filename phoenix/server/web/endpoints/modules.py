from flask import Blueprint, jsonify, render_template, request

from phoenix.server.database import UserModel
from phoenix.server.modules import get_all_module_paths, get_module

modules_bp = Blueprint("modules", __name__, url_prefix="/modules")


@modules_bp.route("/")
@UserModel.authorized
def get_modules():
    use_json = request.args.get("json", "").lower() == "true"
    modules = get_all_module_paths()

    if use_json:
        return jsonify({"status": "success", "modules": modules})
    return render_template("modules.j2", modules=modules)
