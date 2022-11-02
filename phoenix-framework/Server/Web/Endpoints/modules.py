from flask import Blueprint, request, jsonify
from Utils.web import authorized, generate_response, render_template
from Modules import get_all_module_paths, get_module

modules_bp = Blueprint("modules", __name__, url_prefix="/modules")

@modules_bp.route("/")
@authorized
def get_modules():
    use_json = request.args.get("json", "").lower() == "true"
    modules = get_all_module_paths()

    if use_json:
        return jsonify({"status": "success", "modules": modules})
    return render_template("modules.j2", modules=modules)