from flask import Blueprint, request, session

from phoenixc2.server.database import Session, UserModel, LogEntryModel
from phoenixc2.server.utils.misc import Status

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def post_login():
    user = UserModel.get_current_user()

    if user is None:
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        user: UserModel = Session.query(UserModel).filter_by(username=username).first()
        if user is not None and user.check_password(password):
            message = "Logged in via credentials."
        else:
            LogEntryModel.log(
                "danger",
                "auth",
                f"Failed login attempt from {request.remote_addr} "
                f"with username {username}",
                user if user else None,
            )
            return (
                {
                    "status": Status.Error,
                    "message": "Invalid username or password.",
                    "user": None,
                }
            ), 401
    else:
        message = "Logged in via API key."

    session["api_key"] = user._api_key

    return {"status": Status.Success, "message": message, "user": user.to_dict()}


@auth_bp.route("/logout")
@UserModel.authenticated
def logout():
    session.clear()
    return {"status": Status.Success, "message": "Logged out."}
