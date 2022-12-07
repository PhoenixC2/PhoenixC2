from flask import Blueprint, flash, jsonify, redirect, render_template, request, session
from phoenix_framework.server.database import LogEntryModel, Session, UserModel
from phoenix_framework.server.utils.ui import log
from phoenix_framework.server.utils.web import (
    authorized,
    generate_response,
    get_current_user,
)

INVALID_CREDENTIALS = "Invalid username or password."
TEMPLATE = "login.j2"
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET"])
def get_login():
    return render_template(TEMPLATE)


@auth_bp.route("/login", methods=["POST"])
def post_login():
    use_json = request.args.get("json", "").lower() == "true"
    api_key = request.headers.get("Api-Key")
    username = request.form.get("username")
    password = request.form.get("password")

    if api_key is not None:
        user = get_current_user()
        if user is not None:
            LogEntryModel.log("info", "auth", f"Logged in via API key.", Session, user)
            session["id"] = user.id
            session["password"] = user.password_hash
            return generate_response(
                "success", f"Successfully logged in as {user} using Api-Key"
            )
        return generate_response("danger", "Invalid Api-Key.", "login", 400)
    if username is None or password is None:
        return generate_response("danger", "Missing username or password.", "auth", 400)

    user: UserModel = Session.query(UserModel).filter_by(username=username).first()

    if user is None:
        flash(INVALID_CREDENTIALS, "danger")
        return render_template(TEMPLATE, username=username)
    if user.disabled:
        LogEntryModel.log(
            "info",
            "auth",
            f"Attempted to log in as disabled user {user}.",
            Session,
            get_current_user(),
        )
        flash("This user is disabled.", "danger")
        return render_template(TEMPLATE, username=username)
    if user.check_password(password):
        old_user = get_current_user()

        if old_user is not None and old_user.username != username:
            session["id"] = user.id
            session["password"] = user.password_hash
            LogEntryModel.log(
                "info",
                "auth",
                f"Logged in as {'admin' if user.admin else 'user'}  {user}.",
                Session,
                old_user,
            )
            if not use_json:
                flash(f"Changed to {username}.", "success")
                return redirect("/")
            return jsonify(
                {
                    "status": "success",
                    "message": f"Changed to {username}.",
                    "api_key": user.api_key,
                }
            )
        else:
            session["id"] = user.id
            session["password"] = user.password_hash
            LogEntryModel.log(
                "info",
                "auth",
                f"Logged in as {'admin' if user.admin else 'user'} {user}.",
                Session,
                user,
            )
            if not use_json:
                flash(
                    f"Logged in as {'admin' if user.admin else 'user'} {username}.",
                    "success",
                )
                return redirect("/")
            return jsonify(
                {
                    "status": "success",
                    "message": f"Logged in as {username} ({'admin' if user.admin else 'user'}).",
                    "api_key": user.api_key,
                }
            )
    else:
        log(f"Failed to log in as '{user}'.", "danger")
        if not use_json:
            flash(INVALID_CREDENTIALS, "danger")
            return render_template(TEMPLATE, username=username)
        return (
            jsonify({"status": "error", "message": INVALID_CREDENTIALS}),
            401,
        )


@auth_bp.route("/logout")
@authorized
def logout():
    user = get_current_user()
    LogEntryModel.log(
        "info",
        "auth",
        f"{'admin' if user.admin else 'User'} {user} logged out.",
        Session,
        user,
    )
    session.clear()
    return generate_response("success", "Logged out.", "auth/login")
