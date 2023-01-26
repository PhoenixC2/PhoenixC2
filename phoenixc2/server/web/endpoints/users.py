from uuid import uuid1

from flask import Blueprint, jsonify, render_template, request, send_file

from phoenixc2.server.database import LogEntryModel, Session, UserModel
from phoenixc2.server.utils.web import generate_response

INVALID_ID = "Invalid ID."
USER_DOES_NOT_EXIST = "User does not exist."
ENDPOINT = "users"

users_bp = Blueprint(ENDPOINT, __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET"])
@users_bp.route("/<int:user_id>", methods=["GET"])
@UserModel.authorized
def get_users(user_id: int = None):
    use_json = request.args.get("json", "").lower() == "true"
    show_logs = request.args.get("logs", "").lower() == "true"
    show_unseen_logs = request.args.get("unseen", "").lower() == "true"
    show_assigned_operations = (
        request.args.get("assigned_operations", "").lower() == "true"
    )
    show_owned_operations = request.args.get("owned_operations", "").lower() == "true"

    opened_user: UserModel = Session.query(UserModel).filter_by(id=user_id).first()
    users: list[UserModel] = Session.query(UserModel).all()

    if use_json:
        if opened_user is not None:
            return jsonify(
                {
                    "status": "success",
                    "user": opened_user.to_dict(
                        show_logs,
                        show_unseen_logs,
                        show_assigned_operations,
                        show_owned_operations,
                    ),
                }
            )

        return jsonify(
            {
                "status": "success",
                ENDPOINT: [
                    user.to_dict(
                        show_logs,
                        show_unseen_logs,
                        show_assigned_operations,
                        show_owned_operations,
                    )
                    for user in users
                ],
            }
        )
    return render_template(
        "users.j2",
        users=users,
        opened_user=opened_user,
    )


@users_bp.route("/<int:user_id>/picture", methods=["GET"])
@UserModel.authorized
def get_profile_picture(user_id: int):
    user: UserModel = Session.query(UserModel).filter_by(id=user_id).first()
    if user is None:
        return generate_response("error", USER_DOES_NOT_EXIST, ENDPOINT)
    return send_file(user.get_profile_picture(), mimetype="image/png")

@users_bp.route("/picture", methods=["POST"])
@users_bp.route("/<int:user_id>/picture", methods=["POST"])
@UserModel.authorized
def set_profile_picture(user_id: int = None):
    current_user = UserModel.get_current_user()

    if user_id == 1 and current_user.id != 1:
        return generate_response(
            "error", "You can't change the super user's picture.", ENDPOINT
        )
    
    if current_user.admin or current_user.id == user_id:
        user: UserModel = Session.query(UserModel).filter_by(id=user_id).first()
    else:
        return generate_response(
            "error", "You can't change other users' pictures.", ENDPOINT
        )
    
    if user is None:
        return generate_response("error", USER_DOES_NOT_EXIST, ENDPOINT)
    
    if "profile-picture" in request.files:
        profile_picture = request.files["profile-picture"]
        user.set_profile_picture(profile_picture)
    else:
        return generate_response("error", "No profile picture provided.", ENDPOINT)
    Session.commit()
    return generate_response("success", "Profile picture set.", ENDPOINT)

@users_bp.route("/picture", methods=["POST"])
@users_bp.route("/<int:user_id>/picture", methods=["DELETE"])
@UserModel.authorized
def delete_profile_picture(user_id: int = None):
    current_user = UserModel.get_current_user()
    if user_id == 1 and current_user.id != 1:
        return generate_response(
            "error", "You can't change the super user's picture.", ENDPOINT
        )

    if current_user.admin or current_user.id == user_id:
        user: UserModel = Session.query(UserModel).filter_by(id=user_id).first()
    else:
        return generate_response(
            "error", "You can't change other users' pictures.", ENDPOINT
        )

    if user is None:
        return generate_response("error", USER_DOES_NOT_EXIST, ENDPOINT)

    if user.profile_picture:
        user.delete_profile_picture()
    else:
        return generate_response(
            "error", "User doesn't have a profile picture set.", ENDPOINT
        )
    Session.commit()
    return generate_response("success", "Profile picture deleted.", ENDPOINT)


@users_bp.route("/add", methods=["POST"])
@UserModel.admin_required
def add_user():
    use_json = request.args.get("json", "").lower() == "true"
    username = request.form.get("username")
    password = request.form.get("password")
    admin = request.form.get("admin", "") == "on"
    disabled = request.form.get("disabled", "").lower() == "on"

    if not username or not password:
        return generate_response(
            "danger", "Username and password are required.", ENDPOINT, 400
        )

    # Check if user exists
    if Session.query(UserModel).filter_by(username=username).first():
        return generate_response("danger", "User already exists.", ENDPOINT, 403)
    try:
        user = UserModel.create(username, password, admin, disabled)
    except ValueError as e:
        return generate_response("danger", str(e), ENDPOINT, 400)

    if "profile-picture" in request.files:
        profile_picture = request.files["profile-picture"]
        user.set_profile_picture(profile_picture)

    Session.commit()
    LogEntryModel.log(
        "success",
        "users",
        f"{'Admin' if user.admin else 'User'} {username} added.",
        UserModel.get_current_user(),
    )

    if use_json:
        return jsonify(
            {"status": "success", "message": "User added.", "user": user.to_dict()}
        )
    return generate_response("success", "User added.", ENDPOINT)


@users_bp.route("/<int:id>/remove", methods=["DELETE"])
@UserModel.admin_required
def delete_user(id: int = None):
    current_user = UserModel.get_current_user()

    # Check if user exists
    user: UserModel = Session.query(UserModel).filter_by(id=id).first()

    if user is None:
        return generate_response("danger", "User doesn't exist.", ENDPOINT, 400)

    # Check if it's the super user
    if user.id == 1:
        return generate_response(
            "danger", "Can't delete the super user.", ENDPOINT, 403
        )

    # Check if user is the operator
    if user == current_user:
        return generate_response("danger", "Can't delete your own Account.", ENDPOINT)

    # Delete user
    user.delete()
    Session.commit()

    LogEntryModel.log(
        "success",
        "users",
        f"{'Admin' if user.admin else 'User'} {user.username} deleted.",
        current_user,
    )
    return generate_response(
        "success",
        f"Deleted {'Admin' if user.admin else 'User'} {user.username}",
        ENDPOINT,
    )


@users_bp.route("/<int:id>/edit", methods=["PUT"])
@UserModel.admin_required
def edit_user(id: int = None):
    # Get request data
    form_data = dict(request.form)
    current_user = UserModel.get_current_user()

    if id is None:
        if form_data.get("id") is None:
            return generate_response("danger", INVALID_ID, ENDPOINT, 400)
        id = int(form_data.get("id"))
        form_data.pop("id")

    # Check if user exists
    user: UserModel = Session.query(UserModel).filter_by(id=id).first()
    if user is None:
        return generate_response("danger", USER_DOES_NOT_EXIST, ENDPOINT, 400)

    # Check if user is super user
    if user.id == 1 and current_user.id != 1:
        return generate_response("danger", "Can't edit the super user.", ENDPOINT, 403)

    # Edit user
    try:
        user.edit(form_data)
    except Exception as e:
        return generate_response("danger", str(e), ENDPOINT, 500)

    Session.commit()
    
    LogEntryModel.log(
        "success",
        "users",
        f"{'Admin' if user.admin else 'User'} {user.username} edited.",
        current_user,
    )
    return generate_response("success", f"Edited user with ID {id}.", ENDPOINT)


@users_bp.route("/<int:id>/reset_api_key", methods=["PUT", "POST"])
@UserModel.authorized
def reset_api_key(id: int = None):
    use_json = request.args.get("json", "").lower() == "true"
    current_user = UserModel.get_current_user()

    if current_user.id != id and not current_user.admin:
        return generate_response("danger", "Unauthorized", ENDPOINT, 403)

    # Check if user exists
    user: UserModel = Session.query(UserModel).filter_by(id=id).first()

    if user is None:
        return generate_response("danger", "User doesn't exist.", ENDPOINT, 400)

    # Check if user is the super user
    if user.id == 1 and current_user.id != 1:
        return generate_response(
            "danger", "Can't reset the super user's api key.", ENDPOINT, 403
        )

    # Reset API Key
    user.generate_api_key()
    Session.commit()

    LogEntryModel.log(
        "success",
        "users",
        f"{'Admin' if user.admin else 'User'} {user.username}'s API key has been reset.",
        current_user,
    )
    if use_json:
        return jsonify(
            {
                "status": "success",
                "message": "API key has been reset.",
                "api_key": user.api_key,
            }
        )
    return generate_response("success", "API key has been reset.", ENDPOINT)
