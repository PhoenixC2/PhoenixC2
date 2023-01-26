from flask import Blueprint, flash, jsonify, redirect, render_template, request, session

from phoenixc2.server.database import LogEntryModel, Session, UserModel
from phoenixc2.server.utils.ui import log
from phoenixc2.server.utils.web import generate_response

INVALID_CREDENTIALS = "Invalid username or password."
TEMPLATE = "login.j2"
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET"])
def get_login():
    return render_template(TEMPLATE)


@auth_bp.route("/login", methods=["POST"])
def post_login():
    use_json = request.args.get("json", "").lower() == "true"
    api_key = request.headers.get("Api-Key", None)
    username = request.form.get("username", None)
    password = request.form.get("password", None)

    if api_key is not None:
        user = UserModel.get_current_user()
        message = "Logged in via API key."
    else:
        user : UserModel = Session.query(UserModel).filter_by(username=username).first()
        if user is None or not user.check_password(password):
            return generate_response(
                "error",
                INVALID_CREDENTIALS,
                "auth/login",
                401,
            )
        message = "Logged in via credentials."
    
    session["api_key"] = user._api_key

    LogEntryModel.log(
        "success",
        "auth",
        message,
        user,
    )

    if use_json:
        return jsonify({"status": "success", "message": message, "user": user.to_dict()})
    else:
        return generate_response("success", message, "", 200)


@auth_bp.route("/logout")
@UserModel.authorized
def logout():
    user = UserModel.get_current_user()
    LogEntryModel.log(
        "info",
        "auth",
        f"{'admin' if user.admin else 'User'} {user} logged out.",
        user,
    )
    session.clear()
    return generate_response("success", "Logged out.", "auth/login")
