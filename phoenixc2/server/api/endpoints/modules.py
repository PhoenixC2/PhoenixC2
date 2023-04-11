from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander
from flask import Blueprint, request

from phoenixc2.server.database import UserModel
from phoenixc2.server.modules import get_all_module_paths, get_module
from phoenixc2.server.utils.misc import Status


def modules_bp(commander: "Commander"):
    modules_bp = Blueprint("modules", __name__, url_prefix="/modules")

    @modules_bp.route("/")
    @modules_bp.route("/<string:module_name>")
    @UserModel.authenticated
    def get_modules(module_name: str = None):
        full = request.args.get("full", "").lower() == "true"

        modules = get_all_module_paths()
        if module_name is None:
            if full:
                return {
                    "status": Status.Success,
                    "modules": [
                        get_module(module).to_dict(commander) for module in modules
                    ],
                }
            return {"status": Status.Success, "modules": modules}
        else:
            try:
                module = get_module(module_name)
            except ImportError:
                return {"status": Status.Danger, "message": "Module not found."}, 400
        return {"status": Status.Success, "module": module.to_dict(commander)}

    return modules_bp
