from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from phoenixc2.server.commander import Commander
from flask import Blueprint, jsonify, render_template, request

from phoenixc2.server.database import UserModel
from phoenixc2.server.modules import get_all_module_paths, get_module

def modules_bp(commander: "Commander"):
    modules_bp = Blueprint("modules", __name__, url_prefix="/modules")


    @modules_bp.route("/")
    @modules_bp.route("/<string:module_name>")
    @UserModel.authorized
    def get_modules(module_name: str = None):
        use_json = request.args.get("json", "").lower() == "true"

        if module_name is None:
            modules = [get_module(module) for module in modules]
            if use_json:
                return jsonify({"status": "success", "modules": [module.to_dict(commander) for module in modules]})
            return render_template("modules.html", modules=modules, commander=commander)
        else:
            try:
                module = get_module(module_name)
            except ImportError:
                return jsonify({"status": "error", "message": "Module not found."})
            if use_json:
                return jsonify({"status": "success", "module": module.to_dict(commander)})
            return render_template("module.html", module=module, commander=commander)
    return modules_bp