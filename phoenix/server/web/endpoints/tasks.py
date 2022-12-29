from flask import Blueprint, jsonify, render_template, request

from phoenix.server.commander import Commander
from phoenix.server.database import (LogEntryModel, Session, TaskModel,
                                     UserModel)
from phoenix.server.utils.web import generate_response


def tasks_bp(commander: Commander):
    tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

    @tasks_bp.route("/", methods=["GET"])
    @UserModel.authorized
    def get_tasks():
        use_json = request.args.get("json", "") == "true"
        task_query = Session.query(TaskModel)
        tasks: list[TaskModel] = task_query.all()
        if use_json:
            return jsonify([task.to_dict(commander) for task in tasks])
        opened_task = task_query.filter_by(id=request.args.get("open")).first()
        return render_template("tasks.j2", tasks=tasks, opened_task=opened_task)

    @tasks_bp.route("/<string:id>/clear", methods=["POST"])
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

    return tasks_bp
