from flask import Blueprint, jsonify, render_template, request, make_response
from phoenixc2.server.database import OperationModel, Session, UserModel, LogEntryModel
from phoenixc2.server.utils.web import generate_response
from datetime import datetime
INVALID_ID = "Invalid ID."
ENDPOINT = "operations"

operations_bp = Blueprint(ENDPOINT, __name__, url_prefix="/operations")


@operations_bp.route("/", methods=["GET"])
@operations_bp.route("/<int:operation_id>", methods=["GET"])
@UserModel.authorized
def get_operations(operation_id: int = None):
    use_json = request.args.get("json", "").lower() == "true"
    opened_operation = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    operations: list[OperationModel] = Session.query(OperationModel).all()

    if use_json:
        if opened_operation is not None:
            return jsonify(
                {
                    "status": "success",
                    "operation": opened_operation.to_dict(),
                }
            )
        return jsonify(
            {
                "status": "success",
                ENDPOINT: [operation.to_dict() for operation in operations],
            }
        )
    return render_template(
        "operations.j2",
        operations=operations,
        opened_operation=opened_operation,
    )


@operations_bp.route("/add", methods=["POST"])
@UserModel.admin_required
def add_operation():
    name = request.form.get("name", "")
    description = request.form.get("description", "")
    expiry = request.form.get("expiry", None)

    if not name:
        return generate_response("error", "Name is required.", ENDPOINT)
    try:
        operation = OperationModel.add(
            name, description, expiry
        )
        Session.add(operation)
        Session.commit()
    except TypeError as e:
        return generate_response("error", str(e), ENDPOINT)

    LogEntryModel.log(
        "success",
        ENDPOINT,
        f"Operation '{name}' added successfully.",
        UserModel.get_current_user(),
    )
    return generate_response("success", "Operation added successfully.", ENDPOINT)


@operations_bp.route("/<int:operation_id>/edit", methods=["PUT"])
@UserModel.admin_required
def edit_operation(operation_id: int):
    data = request.form
    use_json = request.args.get("json", "").lower() == "true"

    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    if operation is None:
        return generate_response("error", INVALID_ID, ENDPOINT)

    try:
        operation.edit(data)
        Session.commit()
    except Exception as e:
        return generate_response("error", str(e), ENDPOINT)
    LogEntryModel.log(
        "success",
        ENDPOINT,
        f"Operation '{operation.name}' edited successfully.",
        UserModel.get_current_user(),
    )
    if use_json:
        return jsonify({"status": "success", "operation": operation.to_dict()})
    return generate_response("success", "Operation edited successfully.", ENDPOINT)


@operations_bp.route("/<int:operation_id>/remove", methods=["DELETE"])
@UserModel.admin_required
def delete_operation(operation_id: int):
    delete_elements = request.form.get("delete_elements", "").lower() == "true"
    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    if operation is None:
        return generate_response("error", INVALID_ID, ENDPOINT)

    operation.delete(delete_elements)
    Session.commit()

    message = f"Operation '{operation.name}' deleted successfully."
    if delete_elements:
        message += " All associated elements were deleted."
    LogEntryModel.log(
        "success",
        ENDPOINT,
        message,
        UserModel.get_current_user(),
    )
    return generate_response("success", message, ENDPOINT)

@operations_bp.route("/<int:operation_id>/assign", methods=["POST"])
@UserModel.admin_required
def assign_operation(operation_id: int):
    user_id = request.form.get("user_id", None)

    user: UserModel = Session.query(UserModel).filter_by(id=user_id).first()
    if user is None:
        return generate_response("error", INVALID_ID, ENDPOINT)

    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    if operation is None:
        return generate_response("error", INVALID_ID, ENDPOINT)

    operation.assign_user(user)
    Session.commit()
    LogEntryModel.log(
        "success",
        ENDPOINT,
        f"Operation '{operation.name}' assigned to {user.username}.",
        UserModel.get_current_user(),
    )
    return generate_response("success", f"'{user} assigned to '{operation.name}'.", ENDPOINT)

@operations_bp.route("/<int:operation_id>/unassign", methods=["POST"])
@UserModel.admin_required
def unassign_operation(operation_id: int):
    user_id = request.form.get("user_id", None)

    user: UserModel = Session.query(UserModel).filter_by(id=user_id).first()
    if user is None:
        return generate_response("error", INVALID_ID, ENDPOINT)

    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    if operation is None:
        return generate_response("error", INVALID_ID, ENDPOINT)

    operation.unassign_user(user)
    Session.commit()
    LogEntryModel.log(
        "success",
        ENDPOINT,
        f"Operation '{operation.name}' unassigned from {user.username}.",
        UserModel.get_current_user(),
    )
    return generate_response("success", f"'{user} unassigned from '{operation.name}'.", ENDPOINT)

@operations_bp.route("/<int:operation_id>/add_subnet", methods=["POST"])
@UserModel.admin_required
def add_subnet(operation_id: int):
    subnet = request.form.get("subnet", None)

    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    if operation is None:
        return generate_response("error", INVALID_ID, ENDPOINT)
    try:
        operation.add_subnet(subnet)
        Session.commit()
    except Exception as e:
        return generate_response("error", str(e), ENDPOINT)
    LogEntryModel.log(
        "success",
        ENDPOINT,
        f"Subnet '{subnet}' added to '{operation.name}'.",
        UserModel.get_current_user(),
    )
    return generate_response("success", f"Subnet '{subnet}' added to '{operation.name}'.", ENDPOINT)


@operations_bp.route("/<int:operation_id>/remove_subnet", methods=["POST"])
@UserModel.admin_required
def remove_subnet(operation_id: int):
    subnet = request.form.get("subnet", None)

    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    if operation is None:
        return generate_response("error", INVALID_ID, ENDPOINT)
    try:
        operation.remove_subnet(subnet)
        Session.commit()
    except Exception as e:
        return generate_response("error", str(e), ENDPOINT)
    LogEntryModel.log(
        "success",
        ENDPOINT,
        f"Subnet '{subnet}' removed from '{operation.name}'.",
        UserModel.get_current_user(),
    )
    return generate_response("success", f"Subnet '{subnet}' removed from '{operation.name}'.", ENDPOINT)


@operations_bp.route("/<int:operation_id>/change", methods=["PUT"])
@UserModel.admin_required
def change_operation(operation_id: int):
    operation = Session.query(OperationModel).filter_by(id=operation_id).first()
    current_user = UserModel.get_current_user()
    if operation is None:
        return generate_response("error", INVALID_ID, ENDPOINT)
    if current_user not in operation.assigned_users and current_user != operation.owner:
        return generate_response("error", "You are not assigned to this operation.", ENDPOINT)

    LogEntryModel.log(
        "success",
        ENDPOINT,
        f"Operation '{operation.name}' changed successfully.",
        UserModel.get_current_user(),
    )
    response = make_response(generate_response("success", f"Changed operation to '{operation.name}'.", ENDPOINT))
    # set cookie with unlimited expiration
    response.set_cookie("operation", str(operation.id), max_age=60 * 60 * 24 * 365 * 10)
    return response