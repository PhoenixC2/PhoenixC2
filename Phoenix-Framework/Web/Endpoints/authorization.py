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
from Database import db_session, UserModel
from functools import wraps

auth_bp = Blueprint("auth", __name__, url_prefix="/users")


def get_current_user(user_id: int) -> UserModel:
    """Get the user object using the user id"""
    return db_session.query(UserModel).filter_by(user_id=user_id).first()


def authorized(func):
    """Check if a user is logged in and redirect to login page if not"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("id"):
            abort(401)
        else:
            return func(*args, **kwargs)
    return wrapper


def admin(func):
    """Check if a user is admin and redirect to login page if not"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("id"):
            if not get_current_user(session.get("id")).admin:
                abort(403)
            else:
                return func(*args, **kwargs)
        else:
            abort(401)
    return wrapper


@auth_bp.route("login", methods=["GET"])
def get_login():
    return render_template("auth/login.html")


@auth_bp.route("/login", methods=["POST"])
def post_login():
    use_json = request.args.get("json", "").lower() == "true"
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        if not use_json:
            flash("Missing username or password.", "error")
            render_template("auth/login.html")
        return jsonify({"status": "error", "message": "Missing username or passwor.d"})

    user: UserModel = db_session.query(
        UserModel).filter_by(username=username).first()

    if user.disabled:
        log(f"{username} failed to log in because the account is disabled.", "warning")

        if not use_json:
            flash("Account is disabled.", "error")
            redirect("/auth/login")
        return jsonify({"status": "error", "message": "Account is disabled."}), 401

    if user.check_password(password):
        old_user = session.get("username")

        if old_user and old_user != username:
            session["id"] = user.user_id
            log(f"{old_user} changed to {username}.", "success")

            if not use_json:
                flash(f"Changed to {username}.", "success")
                redirect("/")
            return jsonify({"status": "success", "message": f"Changed to {username}."})
        else:
            session["id"] = user.user_id
            log(f"{'Admin' if user.admin else 'User'} {username} logged in.", "success")
            if not use_json:
                flash(
                    f"Logged in as {username} ({'Admin' if user.admin else 'User'}).", "success")
                redirect("/")
            return jsonify({"status": "success", "message": f"Logged in as {username} ({'Admin' if user.admin else 'User'})."})
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
    user = get_current_user(session["id"])
    log(f"{'Admin' if user.admin else 'User'} {user.username} logged out.", "success")
    session.clear()
    if not use_json:
        flash("Logged out", "success")
        redirect("/login")
    return jsonify({"status": "success", "message": "Logged out."})
