from Commander import Commander
from Database import Session, TaskModel
from flask import Blueprint, jsonify, render_template, request, send_file
from Utils.web import authorized, generate_response, get_messages


def tasks_bp(commander: Commander):
    tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

    @tasks_bp.route("/", methods=["GET"])
    @authorized
    def get_tasks():
        use_json = request.args.get("json", "") == "true"
        task_query = Session.query(TaskModel)
        tasks: list[TaskModel] = task_query.all()
        if use_json:
            return jsonify([task.to_dict(commander) for task in tasks])
        opened_task = task_query.filter_by(id=request.args.get("open")).first()
        return render_template("tasks.html", tasks=tasks, opened_task=opened_task, messages=get_messages())
    
    @tasks_bp.route("/clear", methods=["POST"])
    @authorized
    def post_clear_tasks():
        task_id = request.form.get("id", "")
        count = 0
        if task_id == "all":
            for task in Session.query(TaskModel).all():
                if task.finished_at is not None:
                    count += 1
                    Session.delete(task)
        else:
            for task in Session.query(TaskModel).filter_by(device_id=task_id).all():
                if task.finished_at is not None:
                    count += 1
                    Session.delete(task)
        Session.commit()
        return generate_response("success", f"Cleared {count} tasks.", "tasks")

    return tasks_bp