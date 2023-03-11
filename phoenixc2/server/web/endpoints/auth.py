from flask import Blueprint, render_template, request, session, flash

from phoenixc2.server.database import LogEntryModel, Session, UserModel
from phoenixc2.server.utils.misc import Status

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
        user: UserModel = Session.query(UserModel).filter_by(username=username).first()
        if user is None or not user.check_password(password):
            if use_json:
                return (
                    {
                        "status": Status.ERROR,
                        "message": INVALID_CREDENTIALS,
                        "user": None,
                    }
                ), 401
            flash(INVALID_CREDENTIALS, Status.Danger)
            return render_template(TEMPLATE, username=username), 401
        message = "Logged in via credentials."

    session["api_key"] = user._api_key

    LogEntryModel.log(
        Status.Success,
        "auth",
        message,
        user,
    )

    if use_json:
        return {"status": Status.Success, "message": message, "user": user.to_dict()}


@auth_bp.route("/logout")
@UserModel.authenticated
def logout():
    use_json = request.args.get("json", "").lower() == "true"
    user = UserModel.get_current_user()
    LogEntryModel.log(
        Status.Info,
        "auth",
        f"{'admin' if user.admin else 'User'} {user} logged out.",
        user,
    )
    session.clear()
    if use_json:
        return {"status": Status.Success, "message": "Logged out."}
    flash("Logged out.", Status.Success)
    return render_template(TEMPLATE)
