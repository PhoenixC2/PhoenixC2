from flask import Blueprint, make_response, render_template, request, send_file

from phoenixc2.server.database import LogEntryModel, OperationModel, Session, UserModel
from phoenixc2.server.utils.misc import Status

INVALID_ID = "Invalid ID."
ENDPOINT = "operations"

operations_bp = Blueprint(ENDPOINT, __name__, url_prefix="/operations")


@operations_bp.route("/", methods=["GET"])
@operations_bp.route("/<int:operation_id>", methods=["GET"])
@UserModel.authenticated
def get_operations(operation_id: int = None):
    use_json = request.args.get("json", "").lower() == "true"
    show_owner = request.args.get("owner", "").lower() == "true"
    show_assigned_users = request.args.get("assigned", "").lower() == "true"
    show_listeners = request.args.get("listeners", "").lower() == "true"
    show_credentials = request.args.get("credentials", "").lower() == "true"
    show_logs = request.args.get("logs", "").lower() == "true"

    opened_operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    operations: list[OperationModel] = Session.query(OperationModel).all()

    if use_json:
        if opened_operation is not None:
            {
                "status": Status.Success,
                "operation": opened_operation.to_dict(
                    show_owner,
                    show_assigned_users,
                    show_listeners,
                    show_credentials,
                    show_logs,
                ),
            }

        return {
            "status": Status.Success,
            ENDPOINT: [
                operation.to_dict(
                    show_owner,
                    show_assigned_users,
                    show_listeners,
                    show_credentials,
                    show_logs,
                )
                for operation in operations
            ],
        }

    return render_template(
        "operations.j2",
        operations=operations,
        opened_operation=opened_operation,
    )


@operations_bp.route("/current", methods=["GET"])
@UserModel.authenticated
def get_current_operation():
    show_owner = request.args.get("owner", "").lower() == "true"
    show_assigned_users = request.args.get("assigned", "").lower() == "true"
    show_listeners = request.args.get("listeners", "").lower() == "true"
    show_credentials = request.args.get("credentials", "").lower() == "true"
    show_logs = request.args.get("logs", "").lower() == "true"

    current_operation: OperationModel = OperationModel.get_current_operation()

    if current_operation is None:
        return (
            {"status": Status.Danger, "message": "No current operation."},
            400,
        )

    return {
        "status": Status.Success,
        "operation": current_operation.to_dict(
            show_owner,
            show_assigned_users,
            show_listeners,
            show_credentials,
            show_logs,
        ),
    }


@operations_bp.route("/<int:operation_id>/picture", methods=["GET"])
@UserModel.authenticated
def get_picture(operation_id: int):
    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    if operation is None:
        return {"status": Status.Danger, "message": INVALID_ID}, 400

    return send_file(operation.get_picture())


@operations_bp.route("/<int:operation_id>/picture", methods=["POST", "PUT"])
@UserModel.admin_required
def set_picture(operation_id: int):
    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )

    if operation is None:
        return ({"status": Status.Danger, "message": INVALID_ID}), 400

    if "picture" not in request.files:
        return (
            ({"status": Status.Danger, "message": "No picture provided."}),
            400,
        )
    operation.set_picture(request.files["picture"])
    Session.commit()

    LogEntryModel.log(
        Status.Success,
        ENDPOINT,
        f"Operation '{operation.name}' picture updated successfully.",
        UserModel.get_current_user(),
    )
    return {
        "status": Status.Success,
        "message": "Operation picture updated successfully.",
    }


@operations_bp.route("/<int:operation_id>/picture", methods=["DELETE"])
@UserModel.admin_required
def delete_picture(operation_id: int):
    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    if operation is None:
        return ({"status": Status.Danger, "message": INVALID_ID}), 400

    operation.delete_picture()
    Session.commit()
    LogEntryModel.log(
        "success",
        ENDPOINT,
        f"Operation '{operation.name}' picture deleted successfully.",
        UserModel.get_current_user(),
    )
    return {
        "status": Status.Success,
        "message": "Operation picture deleted successfully.",
    }


@operations_bp.route("/add", methods=["POST"])
@UserModel.admin_required
def post_add():
    name = request.form.get("name", "")
    description = request.form.get("description", "")
    expiry = request.form.get("expiry", None)

    if not name:
        return ({"status": Status.Danger, "message": "No name provided."}), 400
    try:
        operation = OperationModel.create(name, description, expiry)
    except TypeError as e:
        return ({"status": Status.Danger, "message": str(e)}), 400

    if "picture" in request.files:
        operation.set_picture(request.files["picture"])

    Session.add(operation)
    Session.commit()

    LogEntryModel.log(
        Status.Success,
        ENDPOINT,
        f"Operation '{name}' added successfully.",
        UserModel.get_current_user(),
    )
    return {
        "status": Status.Success,
        "message": "Operation added successfully.",
        "operation": operation.to_dict(),
    }


@operations_bp.route("/<int:operation_id>/remove", methods=["DELETE"])
@UserModel.admin_required
def delete_remove(operation_id: int):
    delete_elements = request.form.get("delete_elements", "").lower() == "true"

    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    if operation is None:
        return ({"status": Status.Danger, "message": INVALID_ID}), 400

    operation.delete(delete_elements)
    Session.commit()

    message = f"Operation '{operation.name}' deleted successfully."

    if delete_elements:
        message += " All associated elements were deleted."

    LogEntryModel.log(
        Status.Success,
        ENDPOINT,
        message,
        UserModel.get_current_user(),
    )
    return {
        "status": Status.Success,
        "message": message,
    }


@operations_bp.route("/<int:operation_id>/edit", methods=["PUT"])
@UserModel.admin_required
def put_edit(operation_id: int):
    data = request.form

    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )

    if operation is None:
        return ({"status": Status.Danger, "message": INVALID_ID}), 400

    try:
        operation.edit(data)
    except Exception as e:
        return ({"status": Status.Danger, "message": str(e)}), 400

    Session.commit()
    LogEntryModel.log(
        Status.Success,
        ENDPOINT,
        f"Operation '{operation.name}' edited successfully.",
        UserModel.get_current_user(),
    )
    return {"status": "success", "operation": operation.to_dict()}


@operations_bp.route("/<int:operation_id>/assign", methods=["POST"])
@UserModel.admin_required
def post_assign_user(operation_id: int):
    user_id = request.form.get("user_id", None)

    user: UserModel = Session.query(UserModel).filter_by(id=user_id).first()
    if user is None:
        return ({"status": Status.Danger, "message": INVALID_ID}), 400

    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    if operation is None:
        return ({"status": Status.Danger, "message": INVALID_ID}), 400
    try:
        operation.assign_user(user)
    except Exception as e:
        return {"status": Status.Danger, "message": str(e)}, 400

    Session.commit()

    LogEntryModel.log(
        Status.Success,
        ENDPOINT,
        f"Operation '{operation.name}' assigned to {user.username}.",
        UserModel.get_current_user(),
    )
    return {
        "status": Status.Success,
        "message": f"Operation '{operation.name}' assigned to {user.username}.",
    }


@operations_bp.route("/<int:operation_id>/unassign", methods=["DELETE"])
@UserModel.admin_required
def delete_unassign_user(operation_id: int):
    user_id = request.form.get("user_id", None)

    user: UserModel = Session.query(UserModel).filter_by(id=user_id).first()
    if user is None:
        return {"status": Status.Danger, "message": INVALID_ID}

    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    if operation is None:
        return {"status": Status.Danger, "message": INVALID_ID}
    try:
        operation.unassign_user(user)
    except Exception as e:
        return {"status": Status.Danger, "message": str(e)}

    Session.commit()
    LogEntryModel.log(
        "success",
        ENDPOINT,
        f"Operation '{operation.name}' unassigned from {user.username}.",
        UserModel.get_current_user(),
    )
    return {
        "status": Status.Success,
        "message": f"Operation '{operation.name}' unassigned from {user.username}.",
    }


@operations_bp.route("/<int:operation_id>/add_subnet", methods=["POST"])
@UserModel.admin_required
def post_add_subnet(operation_id: int):
    subnet = request.form.get("subnet", None)

    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    if operation is None:
        return {"status": Status.Danger, "message": INVALID_ID}
    try:
        operation.add_subnet(subnet)
    except Exception as e:
        return {"status": Status.Danger, "message": str(e)}

    Session.commit()

    LogEntryModel.log(
        Status.Success,
        ENDPOINT,
        f"Subnet '{subnet}' added to '{operation.name}'.",
        UserModel.get_current_user(),
    )
    return {
        "status": Status.Success,
        "message": f"Subnet '{subnet}' added to '{operation.name}'.",
    }


@operations_bp.route("/<int:operation_id>/remove_subnet", methods=["DELETE"])
@UserModel.admin_required
def delete_remove_subnet(operation_id: int):
    subnet = request.form.get("subnet", None)

    operation: OperationModel = (
        Session.query(OperationModel).filter_by(id=operation_id).first()
    )
    if operation is None:
        return {"status": Status.Danger, "message": INVALID_ID}
    try:
        operation.remove_subnet(subnet)
    except Exception as e:
        return {"status": Status.Danger, "message": str(e)}

    Session.commit()

    LogEntryModel.log(
        "success",
        ENDPOINT,
        f"Subnet '{subnet}' removed from '{operation.name}'.",
        UserModel.get_current_user(),
    )
    return {
        "status": Status.Success,
        "message": f"Subnet '{subnet}' removed from '{operation.name}'.",
    }


@operations_bp.route("/<int:operation_id>/change", methods=["PUT"])
@UserModel.admin_required
def change_operation(operation_id: int):
    operation = Session.query(OperationModel).filter_by(id=operation_id).first()
    current_user = UserModel.get_current_user()

    if operation is None:
        return {"status": Status.Danger, "message": INVALID_ID}

    if current_user not in operation.assigned_users and current_user != operation.owner:
        return {
            "status": Status.Danger,
            "message": "You are not assigned to this operation.",
        }
    LogEntryModel.log(
        "success",
        ENDPOINT,
        f"Operation '{operation.name}' changed successfully.",
        UserModel.get_current_user(),
    )
    response = make_response(
        {
            "status": Status.Success,
            "message": f"Operation '{operation.name}' changed successfully.",
        }
    )
    # set cookie with unlimited expiration
    response.set_cookie("operation", str(operation.id), max_age=60 * 60 * 24 * 365 * 10)
    return response
