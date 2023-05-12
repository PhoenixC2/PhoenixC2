from flask import Blueprint, request

from phoenixc2.server.commander.commander import Commander
from phoenixc2.server.database import (
    LogEntryModel,
    OperationModel,
    Session,
    TaskModel,
    UserModel,
)
from phoenixc2.server.utils.misc import Status


def tasks_bp(commander: Commander):
    blueprint = Blueprint("tasks", __name__, url_prefix="/tasks")

    @blueprint.route("/", methods=["GET"])
    @blueprint.route("/<int:task_id>", methods=["GET"])
    @UserModel.authenticated
    def get_tasks(task_id: int = None):
        show_device = request.args.get("device", "") == "true"
        show_all = request.args.get("all", "") == "true"
        opened_task: TaskModel = Session.query(TaskModel).filter_by(id=task_id).first()

        if show_all or OperationModel.get_current_operation() is None:
            tasks: list[TaskModel] = Session.query(TaskModel).all()
        else:
            tasks: list[TaskModel] = (
                Session.query(TaskModel)
                .filter_by(operation=OperationModel.get_current_operation())
                .all()
            )

        if opened_task is not None:
            return {
                "status": Status.Success,
                "task": opened_task.to_dict(commander, show_device),
            }
        return {
            "status": Status.Success,
            "tasks": [task.to_dict(commander, show_device) for task in tasks],
        }

    @blueprint.route("/<string:task_id>/clear", methods=["DELETE"])
    @UserModel.authenticated
    def delete_clear_tasks(task_id: str = "all"):
        count = 0
        for task in (
            Session.query(TaskModel).all()
            if task_id == "all"
            else Session.query(TaskModel).filter_by(id=task_id).all()
        ):
            if task.finished_at is not None:
                count += 1
                task.delete()
        Session.commit()
        message = f"Cleared {count} task{'s' if count != 1 else ''}."
        if count > 0:
            LogEntryModel.log(
                Status.Info,
                "tasks",
                message,
                UserModel.get_current_user(),
            )
            return {"status": Status.Success, "message": message}
        return {"status": Status.Error, "message": "No tasks were cleared."}

    return blueprint
