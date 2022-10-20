from Utils.web import (admin, authorized, generate_response, get_current_user,
                       get_messages)
from Utils.ui import log
from uuid import uuid1

from Database import Session, UserModel, LogEntryModel
from flask import Blueprint, jsonify, render_template, request

INVALID_ID = "Invalid ID."
USER_DOES_NOT_EXIST = "User does not exist."
ENDPOINT = "users"
users_bp = Blueprint(ENDPOINT, __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET"])
@authorized
def get_users():
    use_json = request.args.get("json", "").lower() == "true"
    curr_user = get_current_user()
    user_query = Session.query(UserModel)
    users: list[UserModel] = user_query.all()
    opened_user = user_query.filter_by(id=request.args.get("open")).first()
    if use_json:
        data = [user.to_dict() for user in users]
        if curr_user.admin:
            for index, user in enumerate(users):
                if user.admin and curr_user.username != "phoenix" \
                        and curr_user.username != user.username:
                    continue
                data[index]["api_key"] = user.api_key

        return jsonify({"status": "success", ENDPOINT: data})
    return render_template("users.j2", user=curr_user, users=users, opened_user=opened_user, messages=get_messages())


@users_bp.route("/add", methods=["POST"])
@admin
def add_user():
    use_json = request.args.get("json", "").lower() == "true"
    username = request.form.get("username")
    password = request.form.get("password")
    admin = request.form.get("admin", "").lower() == "true"
    disabled = request.form.get("disabled", "").lower() == "true"

    if not username or not password:
        return generate_response("danger", "Username and password are required.", ENDPOINT, 400, use_json)

    # Check if user exists
    if Session.query(UserModel).filter_by(username=username).first():
        return generate_response("danger", "User already exists.", ENDPOINT, 403)

    user = UserModel(
        username=username,
        admin=admin,
        disabled=disabled,
        api_key=str(uuid1()))
    user.set_password(password)

    Session.add(user)
    Session.commit()
    LogEntryModel.log(
        "success", "users", f"{'Admin' if user.admin else 'User'} {username} added.", Session, get_current_user())
    if use_json:
        return jsonify({"status": "success", "message": "User added.", "user": user.to_dict()})
    return generate_response("success", "User added.", ENDPOINT)


@users_bp.route("/<int:id>/remove", methods=["DELETE"])
@admin
def delete_user(id: int = None):
    current_user = get_current_user()

    # Check if user exists
    user: UserModel = Session.query(UserModel).filter_by(id=id).first()

    if user is None:
        return generate_response("danger", "User doesn't exist.", ENDPOINT, 400)

    # Check if user is head admin
    if user.username == "phoenix":
        return generate_response("danger", "Can't delete the Phoenix Account.", ENDPOINT, 403)

    # Check if user is the operator
    if user == current_user:
        return generate_response("danger", "Can't delete your own Account.", ENDPOINT)

    # Delete user
    Session.delete(user)
    Session.commit()
    LogEntryModel.log(
        "success", "users", f"{'Admin' if user.admin else 'User'} {user.username} deleted.", Session, current_user)
    return generate_response("success", f"Deleted {'Admin' if user.admin else 'User'} {user.username}", ENDPOINT)


@users_bp.route("/edit", methods=["PUT", "POST"])
@users_bp.route("/<int:id>/edit", methods=["PUT", "POST"])
@admin
def edit_user(id: int = None):
    # Get request data
    form_data = dict(request.form)
    current_user = get_current_user()
    if id is None:
        if form_data.get("id") is None:
            return generate_response("danger", INVALID_ID, ENDPOINT, 400)
        id = int(form_data.get("id"))
        form_data.pop("id")

    # Check if user exists
    user: UserModel = Session.query(
        UserModel).filter_by(id=id).first()
    if user is None:
        return generate_response("danger", USER_DOES_NOT_EXIST, ENDPOINT, 400)

    # Edit user
    try:
        user.edit(form_data)
        Session.commit()
    except Exception as e:
        return generate_response("danger", str(e), ENDPOINT, 500)

    LogEntryModel.log("success", "users", f"{'Admin' if user.admin else 'User'} {user.username} edited.", Session, current_user)
    return generate_response("success", f"Edited user with ID {id}.", ENDPOINT)
