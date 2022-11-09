from flask import Blueprint, flash, jsonify, redirect, render_template, request, session

from phoenix_framework.server.database import LogEntryModel, Session, UserModel
from phoenix_framework.server.utils.ui import log
from phoenix_framework.server.utils.web import (
    authorized,
    generate_response,
    get_current_user,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET"])
def get_login():
    return render_template("login.j2")


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
            session["password"] = user.password
            return generate_response(
                "success", f"Successfully logged in as {user} using Api-Key"
            )
        return generate_response("danger", "Invalid Api-Key.", "login", 400)
    if username is None or password is None:
        return generate_response("danger", "Missing username or password.", "auth", 400)

    user: UserModel = Session.query(UserModel).filter_by(username=username).first()

    if user is None:
        return generate_response(
            "danger", f"User {username} doesn't exist.", "login", 400
        )
    if user.disabled:
        LogEntryModel.log(
            "info",
            "auth",
            f"Attempted to log in as disabled user {user}.",
            Session,
            get_current_user(),
        )
        return generate_response("danger", "Account is disabled.", "login", 401)

    if user.check_password(password):
        old_user = get_current_user()

        if old_user is not None and old_user.username != username:
            session["id"] = user.id
            session["password"] = user.password
            LogEntryModel.log(
                "info", "auth", f"Logged in as {user}.", Session, old_user
            )
            if not use_json:
                flash(f"Changed to {username}.", "success")
                redirect("/")
            return jsonify(
                {
                    "status": "success",
                    "message": f"Changed to {username}.",
                    "api_key": user.api_key,
                }
            )
        else:
            session["id"] = user.id
            session["password"] = user.password
            LogEntryModel.log("info", "auth", f"Logged in as {user}.", Session, user)
            if not use_json:
                flash(
                    f"Logged in as {'Admin' if user.admin else 'User'} {username}.",
                    "success",
                )
                redirect("/")
            return jsonify(
                {
                    "status": "success",
                    "message": f"Logged in as {username} ({'Admin' if user.admin else 'User'}).",
                    "api_key": user.api_key,
                }
            )
    else:
        log(f"Failed to log in as '{user}'.", "danger")
        if not use_json:
            flash("Invalid username or password.", "danger")
            return render_template("login.j2", username=username)
        return (
            jsonify({"status": "error", "message": "Invalid username or password."}),
            401,
        )


@auth_bp.route("/logout")
@authorized
def logout():
    user = get_current_user()
    LogEntryModel.log(
        "info",
        "auth",
        f"{'Admin' if user.admin else 'User'} {user} logged out.",
        Session,
        user,
    )
    session.clear()
    return generate_response("success", "Logged out.", "auth/login")
