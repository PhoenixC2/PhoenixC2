from Database import UserModel, db_session
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, session)
from Utils.ui import log
from Utils.web import authorized, generate_response, get_current_user

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("login", methods=["GET"])
def get_login():
    return render_template("auth/login.html")


@auth_bp.route("/login", methods=["POST"])
def post_login():
    print(dict(request.form))
    use_json = request.args.get("json", "").lower() == "true"
    api_key = request.headers.get("Api-Key")
    username = request.form.get("username")
    password = request.form.get("password")
    if api_key is not None:
        user = get_current_user()
        if user is not None:
            log(f"Logged in as {user} ({'Admin' if user.admin else 'User'}).", "success")
            session["id"] = user.id
            return generate_response("success", f"Successfully logged in as {user} using Api-Key")
        return generate_response("error", "Invalid Api-Key.", "login", 400)
    if username is None or password is None:
        return generate_response("error", "Missing username or password.", "auth", 400)

    user: UserModel = db_session.query(
        UserModel).filter_by(username=username).first()
    if user is None:
        return generate_response("error", f"User {username} doesn't exist.", "login", 400)
    if user.disabled:
        log(f"{username} failed to log in because the account is disabled.", "warning")
        return generate_response("error", "Account is disabled.", "login", 401)

    if user.check_password(password):
        old_user = get_current_user()

        if old_user is not None and old_user.username != username:
            session["id"] = user.id
            log(f"{old_user.username} changed to {username}.", "success")
            if not use_json:
                flash(f"Changed to {username}.", "success")
                redirect("/")
            return jsonify({"status": "success", "message": f"Changed to {username}.", "api_key": user.api_key})
        else:
            session["id"] = user.id
            log(f"{'Admin' if user.admin else 'User'} {username} logged in.", "success")
            if not use_json:
                flash(
                    f"Logged in as {username} ({'Admin' if user.admin else 'User'}).", "success")
                redirect("/")
            return jsonify({"status": "success", "message": f"Logged in as {username} ({'Admin' if user.admin else 'User'}).", "api_key": user.api_key})
    else:
        log(f"{username} failed to log in", "warning")
        if not use_json:
            flash("Invalid username or password.", "error")
            return render_template("auth/login.html", username=username)
        return jsonify({"status": "error", "message": "Invalid username or password."}), 401


@auth_bp.route("/logout")
@authorized
def logout():
    user = get_current_user()
    log(f"{'Admin' if user.admin else 'User'} {user} logged out.", "success")
    session.clear()
    return generate_response("success", "Logged out.")
