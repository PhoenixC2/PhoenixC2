from uuid import uuid1

from Database import Session, LogEntryModel
from flask import (Blueprint, abort, escape, flash, jsonify, redirect,
                   render_template, request, session)
from Utils.ui import log
from Utils.web import admin, authorized, generate_response, get_current_user, get_messages

logs_bp = Blueprint("logs", __name__, url_prefix="/logs")


@logs_bp.route("/", methods=["GET"])
@authorized
def get_logs():
    use_json = request.args.get("json", "").lower() == "true"
    current_user = get_current_user()
    logentry_query = Session.query(LogEntryModel)
    logs: list[LogEntryModel] = logentry_query.all()
    for log in logs:
        log.seen_by_user(current_user)
    Session.commit()
    opened_log = logentry_query.filter_by(id=request.args.get("open")).first()
    if use_json:
        return jsonify({"status": "success", "logs": [log.to_json() for log in logs]}) 
    return render_template("logs.html", user=current_user, logs=logs, opened_log=opened_log, messages=get_messages())


@logs_bp.route("/remove", methods=["DELETE"])
@admin
def delete_user():
    use_json = request.args.get("json", "").lower() == "true"
    username = request.form.get("username")
    current_user = get_current_user()
    if not username:
        if not use_json:
            flash("Username required.")
            abort
        return jsonify({"status": "error", "message": "Username required."})
    # Check if user exists
    user: UserModel = Session.query(UserModel).first()
    if user is None:
        return generate_response("error", "User doesn't exist.", "logs", 400)

    # Check if user is head admin
    if username == "phoenix":
        return generate_response("error", "Can't delete the Phoenix Account.", "logs", 403)

    # Check if user is the operator
    if username == current_user:
        return generate_response("error", "Can't delete your own Account.", "logs")

    # Delete user
    Session.delete(user)
    log(f"({get_current_user().username}) deleted {'Admin' if user.admin else 'User'} {username}.", "success")
    return generate_response("success", f"Deleted {'Admin' if user.admin else 'User'} {username}", "logs")


@logs_bp.route("/edit", methods=["POST"])
@admin
def edit_user():
    use_json = request.args.get("json", "").lower() == "true"
    username = request.form.get("username", "")
    change = request.form.get("change", "").lower()
    value = request.form.get("value", "")
    if not all([username, change, value]) and change != "api-key":
        if not use_json:
            flash("Username, change and value required.", "error")
            return redirect("/logs")
        return jsonify({"status": "error", "message": "Username, change and value required."})
    # Check if user exists
    current_user = get_current_user()
    user: UserModel = Session.query(
        UserModel).filter_by(username=username).first()
    if user is None:
        return generate_response("error", "User doesn't exist.", "logs", 400)

    # Check if user is head admin
    if username == "phoenix" and current_user.username != "phoenix":
        return generate_response("error", "Can't edit the Phoenix Account.", "logs", 403)
    # Edit user
    if change == "admin" and username != "phoenix":
        user.admin = value.lower() == "true"
        Session.commit()
        log(f"({current_user}) updated {username}'s permissions to {'Admin' if user.admin else 'User'}.", "success")
        return generate_response("success", f"Updated {username}'s permissions to {'Admin' if user.admin else 'User'}.", "logs")

    elif change == "password" and len(value) >= 1:
        user.set_password(value)
        Session.commit()
        log(f"({current_user}) updated {username}'s password.", "success")
        return generate_response("success", f"Updated {username}'s password to {value}.", "logs")

    elif change == "username" and username != "phoenix":
        if Session.query(UserModel).filter_by(username=value).first() or value == "":
            return generate_response("error", "Name is already in use.", "logs", 400)
        user = str(escape(value))
        Session.commit()
        log(f"({current_user}) updated {user}'s username to {value}.", "success")
        return generate_response("success", f"Updated {username}'s username to {value}.", "logs")

    elif change == "disabled" and username != "phoenix":
        user.disabled = value.lower() == "true"
        Session.commit()
        log(f"({current_user}) disabled {'Admin' if user.admin else 'User'} {user}", "success")
        return generate_response("success", f"Disabled {user}.", "logs")

    elif change == "api-key":
        user.api_key = str(uuid1())
        log(f"({current_user}) changed {user}'s api-key.")
        if not use_json:
            flash(
                f"Updated {username}'s api-key to {user.api_key}.", "success")
            return redirect("/logs")
        return jsonify({"status": "success", "message": f"Updated {username}'s api-key", "api-key": user.api_key})

    else:
        return generate_response("error", "Invalid change.", "logs", 400)
