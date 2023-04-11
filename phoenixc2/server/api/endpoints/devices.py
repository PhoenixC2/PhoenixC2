from flask import Blueprint, request

from phoenixc2.server.commander.commander import Commander
from phoenixc2.server.database import (
    DeviceModel,
    LogEntryModel,
    OperationModel,
    Session,
    TaskModel,
    UserModel,
)
from phoenixc2.server.utils.misc import Status

TASK_CREATED = "Task created."
DOES_NOT_EXIST = "Device does not exist."


def devices_bp(commander: Commander):
    blueprint = Blueprint("devices", __name__, url_prefix="/devices")

    @blueprint.route("/", methods=["GET"])
    @blueprint.route("/<int:device_id>", methods=["GET"])
    @UserModel.authenticated
    def get_devices(device_id: int = None):
        show_stager = request.args.get("stager", "").lower() == "true"
        show_operation = request.args.get("operation", "").lower() == "true"
        show_tasks = request.args.get("tasks", "").lower() == "true"
        show_all = request.args.get("all", "").lower() == "true"

        opened_device: DeviceModel = (
            Session.query(DeviceModel).filter_by(id=device_id).first()
        )
        if show_all or OperationModel.get_current_operation() is None:
            devices: list[DeviceModel] = Session.query(DeviceModel).all()
        else:
            devices: list[DeviceModel] = Session.query(DeviceModel).filter(
                DeviceModel.operation == OperationModel.get_current_operation()
            )
        if opened_device is not None:
            return {
                "status": Status.Success,
                "device": opened_device.to_dict(
                    commander, show_stager, show_operation, show_tasks
                ),
            }
        return {
            "status": Status.Success,
            "devices": [
                device.to_dict(commander, show_stager, show_operation, show_tasks)
                for device in devices
            ],
        }

    @blueprint.route("/<string:device_id>/clear", methods=["POST"])
    @UserModel.authenticated
    def post_clear_devices(device_id: str = "all"):
        count = 0
        for device in (
            Session.query(DeviceModel).all()
            if device_id == "all"
            else Session.query(DeviceModel).filter_by(id=device_id).all()
        ):
            if not device.connected:
                count += 1
                device.delete()
        Session.commit()
        if count > 0:
            LogEntryModel.log(
                Status.Info,
                "devices",
                f"Cleared {count} devices.",
                UserModel.get_current_user(),
            )
        return {"status": Status.Success, "message": f"Cleared {count} devices."}

    @blueprint.route("/<int:device_id>/reverse_shell", methods=["POST"])
    @UserModel.authenticated
    def post_reverse_shell(device_id: int = None):
        address = request.json.get("address")
        port = request.json.get("port")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=device_id).first()
        if device is None:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": DOES_NOT_EXIST,
                        "task": None,
                    }
                ),
                400,
            )

        try:
            task = TaskModel.reverse_shell(device, address, port)
        except Exception as e:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": str(e),
                        "task": None,
                    }
                ),
                400,
            )

        Session.add(task)
        Session.commit()
        LogEntryModel.log(
            Status.Info,
            "devices",
            "Created reverse shell task.",
            UserModel.get_current_user(),
        )
        return {
            "status": Status.Success,
            "message": TASK_CREATED,
            "task": task.to_dict(commander),
        }

    @blueprint.route("/<int:device_id>/rce", methods=["POST"])
    @UserModel.authenticated
    def post_rce(device_id: int = None):
        cmd = request.json.get("cmd")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=device_id).first()
        if device is None:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": DOES_NOT_EXIST,
                        "task": None,
                    }
                ),
                400,
            )

        try:
            task = TaskModel.remote_command_execution(device, cmd)
        except Exception as e:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": str(e),
                        "task": None,
                    }
                ),
                400,
            )
        Session.add(task)
        Session.commit()
        LogEntryModel.log(
            "info",
            "devices",
            "Created remote command execution task.",
            UserModel.get_current_user(),
        )
        return {
            "status": Status.Success,
            "message": TASK_CREATED,
            "task": task.to_dict(commander),
        }

    @blueprint.route("/<int:device_id>/info", methods=["GET"])
    @UserModel.authenticated
    def get_infos(device_id: int = None):
        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=device_id).first()
        if device is None:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": DOES_NOT_EXIST,
                        "task": None,
                    }
                ),
                400,
            )

        try:
            task = TaskModel.get_infos(device)
        except Exception as e:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": str(e),
                        "task": None,
                    }
                ),
                400,
            )
        Session.add(task)
        Session.commit()
        LogEntryModel.log(
            Status.Info,
            "devices",
            "Created get infos task.",
            UserModel.get_current_user(),
        )
        return {
            "status": Status.Success,
            "message": TASK_CREATED,
            "task": task.to_dict(commander),
        }

    @blueprint.route("/<int:device_id>/dir", methods=["GET"])
    @UserModel.authenticated
    def get_dir(device_id: int = None):
        directory = request.args.get("dir")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=device_id).first()
        if device is None:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": DOES_NOT_EXIST,
                        "task": None,
                    }
                ),
                400,
            )

        try:
            task = TaskModel.list_directory_contents(device, directory)
        except Exception as e:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": str(e),
                        "task": None,
                    }
                ),
                400,
            )
        Session.add(task)
        Session.commit()
        LogEntryModel.log(
            Status.Info,
            "devices",
            "Created list directory contents task.",
            UserModel.get_current_user(),
        )
        return {
            "status": Status.Success,
            "message": TASK_CREATED,
            "task": task.to_dict(commander),
        }

    @blueprint.route("/<int:device_id>/upload", methods=["POST"])
    @UserModel.authenticated
    def post_upload(device_id: int = None):
        target_path = request.args.get("path")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=device_id).first()
        if device is None:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": DOES_NOT_EXIST,
                        "task": None,
                    }
                ),
                400,
            )

        # get file
        file = request.get_data()

        if target_path is None:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": "No target path specified.",
                        "task": None,
                    }
                ),
                400,
            )
        try:
            task = TaskModel.upload(device, file, target_path)
        except Exception as e:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": str(e),
                        "task": None,
                    }
                ),
                400,
            )
        Session.add(task)
        Session.commit()
        LogEntryModel.log(
            "info",
            "devices",
            "Created upload task.",
            UserModel.get_current_user(),
        )
        return {
            "status": Status.Success,
            "message": TASK_CREATED,
            "task": task.to_dict(commander),
        }

    @blueprint.route("/<int:device_id>/download", methods=["GET"])
    @UserModel.authenticated
    def get_download(device_id: int = None):
        target_path = request.args.get("path")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=device_id).first()
        if device is None:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": DOES_NOT_EXIST,
                        "task": None,
                    }
                ),
                400,
            )

        if target_path is None:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": "No target path specified.",
                        "task": None,
                    }
                ),
                400,
            )
        try:
            task = TaskModel.download(device, target_path)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": str(e),
                        "task": None,
                    }
                ),
                400,
            )
        Session.add(task)
        Session.commit()

        LogEntryModel.log(
            Status.Info,
            "devices",
            "Created download task for.",
            UserModel.get_current_user(),
        )

        return {
            "status": Status.Success,
            "message": TASK_CREATED,
            "task": task.to_dict(commander),
        }

    @blueprint.route("/<int:device_id>/module", methods=["POST"])
    @UserModel.authenticated
    def post_execute_module(device_id: int = None):
        path = request.json.get("path")
        execution_method = request.json.get("method")
        data = request.json.get("data", {})

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=device_id).first()
        if device is None:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": DOES_NOT_EXIST,
                        "task": None,
                    }
                ),
                400,
            )

        if path is None:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": "No module path specified.",
                        "task": None,
                    }
                ),
                400,
            )
        try:
            data = dict(data)
        except Exception:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": "Data must be a valid JSON.",
                        "task": None,
                    }
                ),
                400,
            )
        try:
            task = TaskModel.execute_module(device, path, execution_method, data)
        except Exception as e:
            return (
                (
                    {
                        "status": Status.Danger,
                        "message": str(e),
                        "task": None,
                    }
                ),
                400,
            )

        Session.add(task)
        Session.commit()
        LogEntryModel.log(
            "info",
            "devices",
            "Created module execution task.",
            UserModel.get_current_user(),
        )
        return {
            "status": Status.Success,
            "message": TASK_CREATED,
            "task": task.to_dict(commander),
        }

    return blueprint
