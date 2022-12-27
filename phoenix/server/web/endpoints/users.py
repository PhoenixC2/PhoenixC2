from uuid import uuid1

from flask import Blueprint, jsonify, render_template, request, send_file

from phoenix.server.database import LogEntryModel, Session, UserModel
from phoenix.server.utils.web import generate_response

INVALID_ID = "Invalid ID."
USER_DOES_NOT_EXIST = "User does not exist."
ENDPOINT = "users"
users_bp = Blueprint(ENDPOINT, __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET"])
@UserModel.authorized
def get_users():
    use_json = request.args.get("json", "").lower() == "true"
    curr_user = UserModel.get_current_user()
    user_query = Session.query(UserModel)
    users: list[UserModel] = user_query.all()
    opened_user = user_query.filter_by(id=request.args.get("open")).first()
    if use_json:
        data = [user.to_dict() for user in users]
        if curr_user.admin:
            for index, user in enumerate(users):
                if (
                    user.admin_required
                    and curr_user.username != "phoenix"
                    and curr_user.username != user.username
                ):
                    continue
                data[index]["api_key"] = user.api_key

        return jsonify({"status": "success", ENDPOINT: data})
    return render_template(
        "users.j2",
        users=users,
        opened_user=opened_user,
    )


@users_bp.route("/<int:user_id>/profile_picture", methods=["GET"])
@UserModel.authorized
def get_profile_picture(user_id: int):
    user: UserModel = Session.query(UserModel).filter_by(id=user_id).first()
    if user is None:
        return generate_response("error", USER_DOES_NOT_EXIST, ENDPOINT)
    return send_file(user.get_profile_picture(), mimetype="image/png")


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
        user = UserModel.add(username, password, admin, disabled, Session)
    except ValueError as e:
        return generate_response("danger", str(e), ENDPOINT, 400)

    if request.files.get("profile-picture"):
        profile_picture = request.files["profile-picture"]
        user.set_profile_picture(profile_picture)

    Session.commit()
    LogEntryModel.log(
        "success",
        "users",
        f"{'Admin' if user.admin_required else 'User'} {username} added.",
        Session,
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

    # Check if user is head admin
    if user.id == 1:
        return generate_response(
            "danger", "Can't delete the head admin.", ENDPOINT, 403
        )

    # Check if user is the operator
    if user == current_user:
        return generate_response("danger", "Can't delete your own Account.", ENDPOINT)

    # Delete user
    user.delete(Session)

    LogEntryModel.log(
        "success",
        "users",
        f"{'Admin' if user.admin_required else 'User'} {user.username} deleted.",
        Session,
        current_user,
    )
    return generate_response(
        "success",
        f"Deleted {'Admin' if user.admin_required else 'User'} {user.username}",
        ENDPOINT,
    )


@users_bp.route("/edit", methods=["PUT", "POST"])
@users_bp.route("/<int:id>/edit", methods=["PUT", "POST"])
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

    # Check if user is head admin
    if user.id == 1 and current_user.id != 1:
        return generate_response("danger", "Can't edit the head admin.", ENDPOINT, 403)

    # Edit user
    try:
        user.edit(form_data)
        Session.commit()
    except Exception as e:
        return generate_response("danger", str(e), ENDPOINT, 500)

    LogEntryModel.log(
        "success",
        "users",
        f"{'Admin' if user.admin_required else 'User'} {user.username} edited.",
        Session,
        current_user,
    )
    return generate_response("success", f"Edited user with ID {id}.", ENDPOINT)


@users_bp.route("/<int:id>/reset_api_key", methods=["PUT", "POST"])
@UserModel.authorized
def reset_api_key(id: int = None):
    current_user = UserModel.get_current_user()

    if current_user.id != id and not current_user.admin:
        return generate_response("danger", "Unauthorized", ENDPOINT, 403)

    # Check if user exists
    user: UserModel = Session.query(UserModel).filter_by(id=id).first()

    if user is None:
        return generate_response("danger", "User doesn't exist.", ENDPOINT, 400)

    # Check if user is head admin
    if user.id == 1 and current_user.id != 1:
        return generate_response(
            "danger", "Can't reset the head admin's api key.", ENDPOINT, 403
        )

    # Reset API Key
    user.generate_api_key()
    Session.commit()

    LogEntryModel.log(
        "success",
        "users",
        f"{'Admin' if user.admin_required else 'User'} {user.username}'s API key reset.",
        Session,
        current_user,
    )
    return generate_response(
        "success",
        f"Reset {'Admin' if user.admin_required else 'User'} {user.username}'s API key.",
        ENDPOINT,
    )
