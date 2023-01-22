from flask import Blueprint, jsonify, redirect, render_template, request

from phoenixc2.server.database import LogEntryModel, Session, UserModel
from phoenixc2.server.utils.web import generate_response

ENDPOINT = "logs"
logs_bp = Blueprint(ENDPOINT, __name__, url_prefix="/logs")


@logs_bp.route("/", methods=["GET"])
@logs_bp.route("/<int:log_id>", methods=["GET"])
@UserModel.authorized
def get_logs(log_id: int = None):
    use_json = request.args.get("json", "").lower() == "true"
    show_user = request.args.get("user", "").lower() == "true"
    show_unseen_users = request.args.get("unseen", "").lower() == "true"
    show_operation = request.args.get("operation", "").lower() == "true"
    opened_log: LogEntryModel = (
        Session.query(LogEntryModel).filter_by(id=log_id).first()
    )
    logs: list[LogEntryModel] = Session.query(LogEntryModel).all()

    Session.commit()

    if use_json:
        if opened_log is not None:
            return jsonify(
                {
                    "status": "success",
                    "log": opened_log.to_dict(
                        show_user, show_unseen_users, show_operation
                    ),
                }
            )
        return jsonify(
            {
                "status": "success",
                ENDPOINT: [
                    log.to_dict(show_user, show_unseen_users, show_operation)
                    for log in logs
                ],
            }
        )
    return render_template(
        "logs.j2",
        logs=logs,
        opened_log=opened_log,
    )


@logs_bp.route("/read", methods=["GET"])
@UserModel.authorized
def read_logs():
    use_json = request.args.get("json", "").lower() == "true"
    logs = UserModel.get_current_user().read_all_logs()
    Session.commit()

    if use_json:
        return jsonify({"status": "success", ENDPOINT: [log.to_dict() for log in logs]})
    return redirect("/logs")


@logs_bp.route("/<string:log_id>/clear", methods=["POST"])
@UserModel.admin_required
def post_clear_logs(log_id: str = "all"):
    count = 0

    for log in (
        Session.query(LogEntryModel).all()
        if log_id == "all"
        else Session.query(LogEntryModel).filter_by(id=log_id).all()
    ):
        if not log.unseen_users:
            count += 1
            Session.delete(log)
    Session.commit()
    if count > 0:
        LogEntryModel.log(
            "info",
            "logs",
            f"Cleared {count} logs.",
            UserModel.get_current_user(),
        )
    return generate_response("success", f"Cleared {count} log entries.", "logs")
