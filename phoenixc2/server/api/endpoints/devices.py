from flask import Blueprint, request

from phoenixc2.server.commander.commander import Commander
from phoenixc2.server.database import (
    DeviceModel,
    LogEntryModel,
    OperationModel,
    DeviceIdentifierModel,
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
        show_identifier = request.args.get("identifier", "").lower() == "true"
        show_all = request.args.get("all", "").lower() == "true"

        if device_id is not None and device_id != "all":
            device: DeviceModel = (
                Session.query(DeviceModel).filter_by(id=device_id).first()
            )

            if device is None:
                return {"status": Status.Danger, "message": "Device not found."}

            return {
                "status": Status.Success,
                "device": device.to_dict(
                    commander, show_stager, show_operation, show_tasks, show_identifier
                ),
            }

        if show_all or OperationModel.get_current_operation() is None:
            devices: list[DeviceModel] = Session.query(DeviceModel).all()
        else:
            devices: list[DeviceModel] = Session.query(DeviceModel).filter(
                DeviceModel.operation == OperationModel.get_current_operation()
            )
        return {
            "status": Status.Success,
            "devices": [
                device.to_dict(
                    commander, show_stager, show_operation, show_tasks, show_identifier
                )
                for device in devices
            ],
        }

    @blueprint.route("/<string:device_id>/identifier", methods=["GET"])
    @UserModel.authenticated
    def get_device_identifier(device_id: str = None):
        show_device = request.args.get("device", "").lower() == "true"
        show_all = request.args.get("all", "").lower() == "true"

        if device_id is not None and device_id != "all":
            device = Session.query(DeviceModel).filter_by(id=device_id).first()

            if device is None:
                return {"status": Status.Danger, "message": "Device not found."}

            if device.identifier is None:
                return {"status": Status.Danger, "message": "Identifier not found."}

            return {
                "status": Status.Success,
                "identifier": device.identifier.to_dict(commander, show_device),
            }

        if OperationModel.get_current_operation() is None or show_all:
            identifiers = Session.query(DeviceIdentifierModel).all()
        else:
            identifiers = Session.query(DeviceIdentifierModel).filter(
                DeviceIdentifierModel.operation
                == OperationModel.get_current_operation()
            )

        return {
            "status": Status.Success,
            "identifiers": [
                identifier.to_dict(commander, show_device) for identifier in identifiers
            ],
        }

    @blueprint.route("/<string:device_id>/clear", methods=["DELETE"])
    @UserModel.authenticated
    def delete_clear_devices(device_id: str = "all"):
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
        return {"status": Status.Danger, "message": "No devices were cleared."}

    @blueprint.route("/identifiers/<string:identifier_id>/clear", methods=["DELETE"])
    @UserModel.authenticated
    def delete_clear_identifiers(identifier_id: str = "all"):
        count = 0
        for identifier in Session.query(DeviceIdentifierModel).all():
            if identifier.device is None:
                count += 1
                Session.delete(identifier)
        Session.commit()
        if count > 0:
            LogEntryModel.log(
                Status.Info,
                "devices",
                f"Cleared {count} identifiers.",
                UserModel.get_current_user(),
            )
            return {
                "status": Status.Success,
                "message": f"Cleared {count} identifiers.",
            }
        return {"status": Status.Danger, "message": "No identifiers were cleared."}

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

        if not request.data:
            return {
                "status": Status.Danger,
                "message": "File is empty or not provided.",
                "task": None,
            }

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
            task = TaskModel.upload(device, request.data, target_path)
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
