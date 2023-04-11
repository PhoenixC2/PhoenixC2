from flask import Blueprint, request

from phoenixc2.server.database import LogEntryModel, Session, UserModel, OperationModel
from phoenixc2.server.utils.misc import Status

ENDPOINT = "logs"
logs_bp = Blueprint(ENDPOINT, __name__, url_prefix="/logs")


@logs_bp.route("/", methods=["GET"])
@logs_bp.route("/<int:log_id>", methods=["GET"])
@UserModel.authenticated
def get_logs(log_id: int = None):
    show_user = request.args.get("user", "").lower() == "true"
    show_unseen_users = request.args.get("unseen", "").lower() == "true"
    show_operation = request.args.get("operation", "").lower() == "true"
    show_all = request.args.get("all", "").lower() == "true"
    status_filter = request.args.get("status", "").lower()

    opened_log: LogEntryModel = (
        Session.query(LogEntryModel).filter_by(id=log_id).first()
    )

    if show_all or OperationModel.get_current_operation() is None:
        logs: list[LogEntryModel] = Session.query(LogEntryModel).all()

        if status_filter:
            logs: list[LogEntryModel] = (
                Session.query(LogEntryModel).filter_by(status=status_filter).all()
            )
        else:
            logs: list[LogEntryModel] = Session.query(LogEntryModel).all()

    else:
        logs: list[LogEntryModel] = (
            Session.query(LogEntryModel)
            .filter_by(operation=OperationModel.get_current_operation())
            .all()
        )

    if opened_log is not None:
        return {
            "status": Status.Success,
            "log": opened_log.to_dict(show_user, show_unseen_users, show_operation),
        }
    return {
        "status": Status.Success,
        ENDPOINT: [
            log.to_dict(show_user, show_unseen_users, show_operation) for log in logs
        ],
    }


@logs_bp.route("/read", methods=["GET"])
@UserModel.authenticated
def get_read_logs():
    curr_user = UserModel.get_current_user()

    logs = curr_user.unseen_logs
    curr_user.unseen_logs.clear()
    Session.commit()

    return {"status": Status.Success, ENDPOINT: [log.to_dict() for log in logs]}


@logs_bp.route("/<string:log_id>/clear", methods=["DELETE"])
@UserModel.admin_required
def delete_clear_logs(log_id: str = "all"):
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

    if Session.query(LogEntryModel).count() != 0:
        message = (
            f"Cleared {count} log entr{'ies' if count != 1 else 'y'}. "
            "Some logs were't seen by all users."
        )
    else:
        message = f"Cleared {count} log entr{'ies' if count != 1 else 'y'}."
    if count > 0:
        LogEntryModel.log(
            Status.Info,
            "logs",
            message,
            UserModel.get_current_user(),
        )
    return {"status": Status.Success, "message": message}
