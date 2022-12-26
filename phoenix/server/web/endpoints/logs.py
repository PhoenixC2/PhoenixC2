from flask import Blueprint, jsonify, redirect, render_template, request

from phoenix_framework.server.database import LogEntryModel, Session
from phoenix_framework.server.utils.web import (admin, authorized,
                                                generate_response,
                                                get_current_user)

ENDPOINT = "logs"
logs_bp = Blueprint(ENDPOINT, __name__, url_prefix="/logs")


@logs_bp.route("/", methods=["GET"])
@authorized
def get_logs():
    use_json = request.args.get("json", "").lower() == "true"
    logentry_query = Session.query(LogEntryModel)
    logs: list[LogEntryModel] = logentry_query.all()
    get_current_user().read_all_logs()  # mark all logs as seen
    Session.commit()
    opened_log = logentry_query.filter_by(id=request.args.get("open")).first()
    if use_json:
        return jsonify({"status": "success", ENDPOINT: [log.to_dict() for log in logs]})
    return render_template(
        "logs.j2",
        logs=logs,
        opened_log=opened_log,
    )


@logs_bp.route("/read", methods=["GET"])
@authorized
def read_logs():
    use_json = request.args.get("json", "").lower() == "true"
    user = get_current_user()
    logs = user.unseen_logs
    user.read_all_logs()
    Session.commit()
    if use_json:
        return jsonify({"status": "success", ENDPOINT: [log.to_dict() for log in logs]})
    return redirect("/logs")


@logs_bp.route("/<string:id>/clear", methods=["POST"])
@admin
def post_clear_devices(id: str = "all"):
    count = 0

    for log in (
        Session.query(LogEntryModel).all()
        if id == "all"
        else Session.query(LogEntryModel).filter_by(id=id).all()
    ):
        if not log.unseen_users:
            count += 1
            Session.delete(log)
    Session.commit()
    if count > 0:
        LogEntryModel.log(
            "info", "logs", f"Cleared {count} logs.", Session, get_current_user()
        )
    return generate_response("success", f"Cleared {count} log entries.", "logs")
