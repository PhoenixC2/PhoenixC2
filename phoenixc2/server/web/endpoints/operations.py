from flask import Blueprint, jsonify, render_template, request

from phoenixc2.server.database import OperationModel, Session, UserModel
from phoenixc2.server.utils.web import generate_response

INVALID_ID = "Invalid ID."
USER_DOES_NOT_EXIST = "User does not exist."
ENDPOINT = "operations"

operations_bp = Blueprint(ENDPOINT, __name__, url_prefix="/operations")


@operations_bp.route("/", methods=["GET"])
@UserModel.authorized
def get_operations():
    use_json = request.args.get("json", "").lower() == "true"
    curr_user = UserModel.get_current_user()
    operation_query = Session.query(OperationModel)
    operations: list[OperationModel] = operation_query.all()
    opened_operation = operation_query.filter_by(id=request.args.get("open")).first()
    if use_json:
        data = [operation.to_dict() for operation in operations]
        if curr_user.admin:
            for index, operation in enumerate(operations):
                if (
                    operation.admin
                    and curr_user.username != "phoenix"
                    and curr_user.username != operation.username
                ):
                    continue
                data[index]["api_key"] = operation.api_key

        return jsonify({"status": "success", ENDPOINT: data})
    return render_template(
        "operations.j2",
        operations=operations,
        opened_operation=opened_operation,
    )


@operations_bp.route("/add", methods=["POST"])
@UserModel.admin_required
def add_operation():
    OperationModel.add()