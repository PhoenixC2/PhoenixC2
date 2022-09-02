from flask import (
    Blueprint,
    abort,
    session,
    request,
    render_template,
    jsonify,
    redirect,
    flash,
    escape)
from Utils.ui import log
from Utils.web import get_current_user, authorized, generate_response
from Database import db_session, UserModel

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("login", methods=["GET"])
def get_login():
    return render_template("auth/login.html")


@auth_bp.route("/login", methods=["POST"])
def post_login():
    use_json = request.args.get("json", "").lower() == "true"
    api_key = request.headers.get("Api-Key")
    username = request.form.get("username")
    password = request.form.get("password")
    if api_key is not None:
        user = get_current_user()
        if user is not None:
            log(f"Logged in as {user} ({'Admin' if user.admin else 'User'}).", "success")
            session["id"] = user.user_id
            return generate_response(use_json, "success", f"Successfully logged in as {user} using Api-Key")
        return generate_response(use_json, "error", "Invalid Api-Key.", "login", 400)
    if username is None or password is None:
        return generate_response(use_json, "error", "Missing username or password.", "auth", 400)

    user: UserModel = db_session.query(
        UserModel).filter_by(username=username).first()

    if user.disabled:
        log(f"{username} failed to log in because the account is disabled.", "warning")
        return generate_response(use_json, "error", "Account is disabled.", "login", 401)

    if user.check_password(password):
        old_user = get_current_user()

        if old_user is not None and old_user.username != username:
            session["id"] = user.user_id
            log(f"{old_user.username} changed to {username}.", "success")
            if not use_json:
                flash(f"Changed to {username}.", "success")
                redirect("/")
            return jsonify({"status": "success", "message": f"Changed to {username}.", "api_key": user.api_key})
        else:
            session["id"] = user.user_id
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
    use_json = request.args.get("json", "").lower() == "true"
    user = get_current_user()
    log(f"{'Admin' if user.admin else 'User'} {user} logged out.", "success")
    session.clear()
    return generate_response(use_json, "success", "Logged out.")
