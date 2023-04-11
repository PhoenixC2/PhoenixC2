from flask import Blueprint, request

from phoenixc2.server.commander.commander import Commander
from phoenixc2.server.database import (
    ListenerModel,
    LogEntryModel,
    OperationModel,
    Session,
    UserModel,
)
from phoenixc2.server.utils.misc import Status, get_network_interfaces
from phoenixc2.server.utils.ui import log

INVALID_ID = "Invalid ID."
LISTENER_DOES_NOT_EXIST = "Listener does not exist."
ENDPOINT = "listeners"


def listeners_bp(commander: Commander):
    blueprint = Blueprint(ENDPOINT, __name__, url_prefix="/listeners")

    @blueprint.route("/", methods=["GET"])
    @blueprint.route("/<int:listener_id>", methods=["GET"])
    @UserModel.authenticated
    def get_listeners(listener_id: int = None):
        show_operation = request.args.get("show_operation", "").lower() == "true"
        show_stagers = request.args.get("show_stagers", "").lower() == "true"
        show_all = request.args.get("all", "").lower() == "true"
        opened_listener = Session.query(ListenerModel).filter_by(id=listener_id).first()

        if show_all or OperationModel.get_current_operation() is None:
            listeners: list[ListenerModel] = Session.query(ListenerModel).all()
        else:
            listeners = OperationModel.get_current_operation().listeners
        if opened_listener is not None:
            return {
                "status": Status.Success,
                "listener": opened_listener.to_dict(
                    commander, show_operation, show_stagers
                ),
            }
        return {
            "status": Status.Success,
            ENDPOINT: [
                listener.to_dict(commander, show_operation, show_stagers)
                for listener in listeners
            ],
        }

    @blueprint.route("/available", methods=["GET"])
    @UserModel.authenticated
    def get_available():
        listeners = {}
        type = request.args.get("type")
        try:
            if type == "all" or type is None:
                for listener in ListenerModel.get_all_classes():
                    listeners[listener.name] = listener.to_dict(commander)
            else:
                listeners[type] = ListenerModel.get_class_from_type(type).to_dict(
                    commander
                )
        except Exception as e:
            return ({"status": Status.Danger, "message": str(e)}), 400
        else:
            return {"status": Status.Success, "listeners": listeners}

    @blueprint.route("/add", methods=["POST"])
    @UserModel.authenticated
    def post_add():
        # Get request data
        listener_type = request.json.get("type")
        is_interface = request.args.get("is_interface", "").lower() == "true"
        data = dict(request.json)

        if is_interface:
            interfaces = get_network_interfaces()
            if data.get("address", "") in interfaces:
                data["address"] = interfaces[data["address"]]
            else:
                return {
                    "status": Status.Danger,
                    "message": "Invalid network interface.",
                }, 400
        try:
            # Check if data is valid and clean it
            data = ListenerModel.get_class_from_type(
                listener_type
            ).option_pool.validate_all(data)
        except Exception as e:
            return ({"status": Status.Danger, "message": str(e)}), 400

        # Add listener
        try:
            # has to be added again bc it got filtered out
            data["type"] = listener_type
            listener = ListenerModel.create_from_data(data)
        except Exception as e:
            return ({"status": Status.Danger, "message": str(e)}), 400
        Session.add(listener)
        Session.commit()
        LogEntryModel.log(
            Status.Success,
            "listeners",
            f"Added listener '{listener.name}' ({listener.type})",
            UserModel.get_current_user(),
        )
        return (
            (
                {
                    "status": Status.Success,
                    "message": "Listener added successfully.",
                    "listener": listener.to_dict(commander),
                }
            ),
            201,
        )

    @blueprint.route("/<int:listener_id>/remove", methods=["DELETE"])
    @UserModel.authenticated
    def delete_remove(listener_id: int):
        # Get request data
        stop = request.json.get("stop", "").lower() != "false"

        # Check if listener exists
        listener: ListenerModel = (
            Session.query(ListenerModel).filter_by(id=listener_id).first()
        )
        if listener is None:
            return {"status": Status.Danger, "message": LISTENER_DOES_NOT_EXIST}, 400
        name = listener.name
        type = listener.type
        listener.delete(stop, commander)
        message = "Listener deleted and stopped" if stop else "Listener deleted"
        Session.commit()
        LogEntryModel.log(
            Status.Success,
            "listeners",
            f"{message} '{name}' ({type})",
            UserModel.get_current_user(),
        )
        return {
            "status": Status.Success,
            "message": f"{message} successfully.",
            "listener": listener.to_dict(commander),
        }

    @blueprint.route("/<int:listener_id>/edit", methods=["PUT"])
    @UserModel.authenticated
    def put_edit(listener_id: int = None):
        # Get request data
        form_data = dict(request.json)

        if listener_id is None:
            if form_data.get("id") is None:
                return ({"status": Status.Danger, "message": INVALID_ID}), 400
            listener_id = int(form_data.get("id"))
            form_data.pop("id")

        # Check if listener exists
        listener: ListenerModel = (
            Session.query(ListenerModel).filter_by(id=listener_id).first()
        )
        if listener is None:
            return {"status": Status.Danger, "message": LISTENER_DOES_NOT_EXIST}, 400

        # check if port is the same to avoid validation error
        if form_data.get("port", "") == str(listener.port):
            form_data.pop("port")

        # Edit listener
        try:
            listener.edit(form_data)
        except Exception as e:
            return ({"status": Status.Danger, "message": str(e)}), 400

        Session.commit()
        LogEntryModel.log(
            Status.Success,
            "listeners",
            f"Edited listener '{listener.name}' ({listener.type})",
            UserModel.get_current_user(),
        )
        return {
            "status": Status.Success,
            "message": "Listener edited successfully.",
            "listener": listener.to_dict(commander),
        }

    @blueprint.route("/<int:listener_id>/start", methods=["POST"])
    @UserModel.authenticated
    def post_start(listener_id: int):
        # Check if listener exists
        listener: ListenerModel = (
            Session.query(ListenerModel).filter_by(id=listener_id).first()
        )

        if listener is None:
            return {"status": Status.Danger, "message": LISTENER_DOES_NOT_EXIST}, 400

        log(
            f"({UserModel.get_current_user().username}) "
            f"Starting Listener with ID {listener_id}",
            Status.Info,
        )

        try:
            message = listener.start(commander)
        except Exception as e:
            LogEntryModel.log(
                Status.Danger,
                "listeners",
                message,
                UserModel.get_current_user(),
            )
            return ({"status": Status.Danger, "message": str(e)}), 400
        else:
            LogEntryModel.log(
                Status.Success,
                "listeners",
                message,
                UserModel.get_current_user(),
            )
            return {
                "status": Status.Success,
                "message": "Listener started successfully.",
                "listener": listener.to_dict(commander),
            }

    @blueprint.route("/<int:listener_id>/stop", methods=["POST"])
    @UserModel.authenticated
    def post_stop(listener_id: int):
        # Check if listener exists
        listener: ListenerModel = (
            Session.query(ListenerModel).filter_by(id=listener_id).first()
        )

        if listener is None:
            return {"status": Status.Danger, "message": LISTENER_DOES_NOT_EXIST}, 400

        log(
            f"({UserModel.get_current_user().username})"
            f"Stopping Listener with ID {listener_id}",
            "info",
        )

        try:
            listener.stop(commander)
        except Exception as e:
            return ({"status": Status.Danger, "message": str(e)}), 400
        else:
            LogEntryModel.log(
                Status.Success,
                "listeners",
                f"Stopped listener '{listener.name}' ({listener.type})",
                UserModel.get_current_user(),
            )
        return {
            "status": Status.Success,
            "message": "Stopped listener successfully.",
            "listener": listener.to_dict(commander),
        }

    @blueprint.route("/<int:listener_id>/restart", methods=["POST"])
    @UserModel.authenticated
    def post_restart(listener_id: int):
        # Check if listener exists
        listener: ListenerModel = (
            Session.query(ListenerModel).filter_by(id=listener_id).first()
        )

        try:
            log(
                f"({UserModel.get_current_user().username}) "
                f"Restarting listener with ID {listener_id}.",
                "info",
            )
            listener.restart(commander)
        except Exception as e:
            LogEntryModel.log(
                "danger",
                "listeners",
                f"Failed to restart listener '{listener.name}' "
                f"({listener.type}): {str(e)}",
                UserModel.get_current_user(),
            )
            return ({"status": Status.Danger, "message": str(e)}), 400
        else:
            LogEntryModel.log(
                Status.Success,
                "listeners",
                f"Restarted listener '{listener.name}' ({listener.type})",
                UserModel.get_current_user(),
            )

        return {
            "status": Status.Success,
            "message": "Restarted listener successfully.",
            "listener": listener.to_dict(commander),
        }

    return blueprint
