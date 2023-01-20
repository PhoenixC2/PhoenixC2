from flask import Blueprint, jsonify, render_template, request

from phoenixc2.server.commander import Commander
from phoenixc2.server.database import (LogEntryModel, Session, TaskModel,
                                     UserModel)
from phoenixc2.server.utils.web import generate_response


def tasks_bp(commander: Commander):
    blueprint = Blueprint("tasks", __name__, url_prefix="/tasks")

    @blueprint.route("/", methods=["GET"])
    @UserModel.authorized
    def get_tasks():
        use_json = request.args.get("json", "") == "true"
        opened_task = Session.query(TaskModel).filter_by(id=request.args.get("open")).first()
        tasks: list[TaskModel] = Session.query(TaskModel).all()
        if use_json:
            return jsonify([task.to_dict(commander) for task in tasks])
        return render_template("tasks.j2", tasks=tasks, opened_task=opened_task)

    @blueprint.route("/<string:id>/clear", methods=["POST"])
    @UserModel.authorized
    def post_clear_tasks(id: str = "all"):
        count = 0
        for task in (
            Session.query(TaskModel).all()
            if id == "all"
            else Session.query(TaskModel).filter_by(id=id).all()
        ):
            if task.finished_at is not None:
                count += 1
                Session.delete(task)
        Session.commit()
        if count > 0:
            LogEntryModel.log(
                "info",
                "tasks",
                f"Cleared {count} tasks.",
                UserModel.get_current_user(),
            )
        return generate_response("success", f"Cleared {count} tasks.", "tasks")

    return blueprint
