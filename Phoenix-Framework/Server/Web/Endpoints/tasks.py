from Commander import Commander
from Database import db_session, TasksModel
from flask import Blueprint, jsonify, render_template, request, send_file
from Utils.web import authorized, generate_response


def tasks_bp(commander: Commander):
    tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

    @tasks_bp.route("/", methods=["GET"])
    @authorized
    def get_tasks():
        use_json = request.args.get("json", "") == "true"
        task_query = db_session.query(TasksModel)
        tasks: list[TasksModel] = task_query.all()
        if use_json:
            return jsonify([task.to_json(commander) for task in tasks])
        opened_task = task_query.filter_by(id=request.args.get("open")).first()
        return render_template("tasks.html", tasks=tasks, opened_task=opened_task)
    
    return tasks_bp