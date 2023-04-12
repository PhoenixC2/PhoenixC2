from flask import Blueprint, request, session

from phoenixc2.server.database import Session, UserModel, LogEntryModel
from phoenixc2.server.utils.misc import Status

INVALID_CREDENTIALS = "Invalid username or password."
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def post_login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username is None or password is None:
        user = UserModel.get_current_user()
        message = "Logged in via API key."
    else:
        user: UserModel = Session.query(UserModel).filter_by(username=username).first()
    if user is None or not user.check_password(password):
        LogEntryModel.log(
            "danger",
            "auth",
            f"Failed login attempt from {request.remote_addr} with username {username}",
            user if user else None,
        )
        return (
            {
                "status": Status.Error,
                "message": INVALID_CREDENTIALS,
                "user": None,
            }
        ), 401
    message = "Logged in via credentials."

    session["api_key"] = user._api_key

    return {"status": Status.Success, "message": message, "user": user.to_dict()}


@auth_bp.route("/logout")
@UserModel.authenticated
def logout():
    session.clear()
    return {"status": Status.Success, "message": "Logged out."}
