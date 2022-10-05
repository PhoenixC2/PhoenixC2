from Database import LogEntryModel, Session
from flask import (Blueprint, abort, escape, flash, jsonify, redirect,
                   render_template, request, session)
from Utils.ui import log
from Utils.web import (admin, authorized, generate_response, get_current_user,
                       get_messages)

LOGS = "logs"
logs_bp = Blueprint(LOGS, __name__, url_prefix="/logs")


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
        return jsonify({"status": "success", LOGS: [log.to_dict() for log in logs]})
    return render_template("logs.html", user=current_user, logs=logs, opened_log=opened_log, messages=get_messages())


@logs_bp.route("/clear", methods=["POST"])
@admin
def post_clear_devices():
    log_id = request.form.get("id", "")
    count = 0
    if log_id == "all":
        for log in Session.query(LogEntryModel).all():
            if not log.unseen_users:
                count += 1
                Session.delete(log)
    else:
        for log in Session.query(LogEntryModel).filter_by(device_id=log_id).all():
            if not log.unseen_users:
                count += 1
                Session.delete(log)
    Session.commit()
    return generate_response("success", f"Cleared {count} log entries.", "logs")
