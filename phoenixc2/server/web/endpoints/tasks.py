from flask import Blueprint, jsonify, render_template, request

from phoenixc2.server.commander import Commander
from phoenixc2.server.database import (LogEntryModel, Session, TaskModel,
                                       UserModel)
from phoenixc2.server.utils.web import generate_response


def tasks_bp(commander: Commander):
    blueprint = Blueprint("tasks", __name__, url_prefix="/tasks")

    @blueprint.route("/", methods=["GET"])
    @blueprint.route("/<int:task_id>", methods=["GET"])
    @UserModel.authorized
    def get_tasks(task_id: int = None):
        use_json = request.args.get("json", "") == "true"
        show_device = request.args.get("device", "") == "true"
        opened_task: TaskModel = Session.query(TaskModel).filter_by(id=task_id).first()
        tasks: list[TaskModel] = Session.query(TaskModel).all()
        if use_json:
            if opened_task is not None:
                return jsonify(
                    {
                        "status": "success",
                        "task": opened_task.to_dict(commander, show_device),
                    }
                )
            return jsonify(
                {
                    "status": "success",
                    "tasks": [task.to_dict(commander, show_device) for task in tasks],
                }
            )
        return render_template("tasks.j2", tasks=tasks, opened_task=opened_task)

    @blueprint.route("/<string:task_id>/clear", methods=["POST"])
    @UserModel.authorized
    def post_clear_tasks(task_id: str = "all"):
        count = 0
        for task in (
            Session.query(TaskModel).all()
            if task_id == "all"
            else Session.query(TaskModel).filter_by(id=task_id).all()
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
