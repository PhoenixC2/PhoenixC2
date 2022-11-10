from flask import Blueprint, jsonify, render_template, request

from phoenix_framework.server.commander import Commander
from phoenix_framework.server.creator.listener import (add_listener,
                                                       restart_listener,
                                                       start_listener,
                                                       stop_listener)
from phoenix_framework.server.database import (ListenerModel, LogEntryModel,
                                               Session)
from phoenix_framework.server.utils.misc import (get_network_interfaces,
                                                 get_platform)
from phoenix_framework.server.utils.ui import log
from phoenix_framework.server.utils.web import (authorized, generate_response,
                                                get_current_user)

INVALID_ID = "Invalid ID."
LISTENER_DOES_NOT_EXIST = "Listener does not exist."
ENDPOINT = "listeners"


def listeners_bp(commander: Commander):
    listeners_bp = Blueprint(ENDPOINT, __name__, url_prefix="/listeners")

    @listeners_bp.route("/", methods=["GET"])
    @authorized
    def get_listeners():
        use_json = request.args.get("json", "").lower() == "true"
        listener_query = Session.query(ListenerModel)
        listener_types = ListenerModel.get_all_listener_classes()
        listeners: list[ListenerModel] = listener_query.all()
        if use_json:
            return jsonify([listener.to_dict(commander) for listener in listeners])
        opened_listener = listener_query.filter_by(id=request.args.get("open")).first()
        return render_template(
            "listeners.j2",
            listeners=listeners,
            opened_listener=opened_listener,
            commander=commander,
            listener_types=listener_types,
            network_interfaces=get_network_interfaces(),
            platform=get_platform(),
        )

    @listeners_bp.route("/available", methods=["GET"])
    @authorized
    def get_available():
        listeners = {}
        type = request.args.get("type")
        try:
            if type == "all" or type is None:
                for listener in ListenerModel.get_all_listener_classes():
                    listeners[listener.name] = listener.to_dict(commander)
            else:
                listeners[type] = ListenerModel.get_listener_class_from_type(
                    type
                ).to_dict(commander)
        except Exception as e:
            return generate_response("danger", str(e), ENDPOINT, 400)
        else:
            return jsonify(listeners)

    @listeners_bp.route("/add", methods=["POST"])
    @authorized
    def post_add():
        # Get request data
        use_json = request.args.get("json", "").lower() == "true"
        listener_type = request.form.get("type")
        name = request.form.get("name")
        is_interface = request.args.get("is_interface", "").lower() == "true"
        data = dict(request.form)
        if is_interface:
            interfaces = get_network_interfaces()
            if data.get("address", "") in interfaces:
                data["address"] = interfaces[data["address"]]
            else:
                return generate_response(
                    "danger", "Invalid network interface.", ENDPOINT, 400
                )
        try:
            # Check if data is valid and clean it
            data = ListenerModel.get_listener_class_from_type(
                listener_type
            ).options.validate_all(data)
        except Exception as e:
            return generate_response("danger", str(e), ENDPOINT, 400)

        # Add listener
        try:
            # has to be added again bc it got filtered out by options.validate_data(data)
            data["type"] = listener_type
            listener = add_listener(data)
        except Exception as e:
            return generate_response("danger", str(e), ENDPOINT, 500)
        LogEntryModel.log(
            "success",
            "listeners",
            f"Added listener '{listener.name}' ({listener.type})",
            Session,
            get_current_user(),
        )
        if use_json:
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": "Listener added successfully.",
                        "listener": listener.to_dict(commander),
                    }
                ),
                201,
            )
        return generate_response(
            "success", f"Created Listener {name} ({listener_type}).", ENDPOINT
        )

    @listeners_bp.route("/<int:id>/remove", methods=["DELETE"])
    @authorized
    def delete_remove(id: int):
        # Get request data
        stop = request.form.get("stop", "").lower() != "false"

        # Check if listener exists
        listener: ListenerModel = Session.query(ListenerModel).filter_by(id=id).first()
        if listener is None:
            return generate_response("danger", LISTENER_DOES_NOT_EXIST, ENDPOINT, 400)

        if stop and listener.is_active(commander):
            stop_listener(listener, commander)
            listener.delete_stagers(Session)
            Session().delete(listener)
            Session().commit()
            LogEntryModel.log(
                "success",
                "listeners",
                f"Deleted and stopped listener '{listener.name}' ({listener.type})",
                Session,
                get_current_user(),
            )
            return generate_response(
                "success", f"Deleted and stopped listener with ID {id}.", ENDPOINT
            )

        listener.delete_stagers(Session)
        Session().delete(listener)
        Session().commit()
        LogEntryModel.log(
            "success",
            "listeners",
            f"Deleted listener '{listener.name}' ({listener.type})",
            Session,
            get_current_user(),
        )
        return generate_response("success", f"Deleted listener with ID {id}.", ENDPOINT)

    @listeners_bp.route("/edit", methods=["PUT", "POST"])
    @listeners_bp.route("/<int:id>/edit", methods=["PUT", "POST"])
    @authorized
    def put_edit(id: int = None):
        # Get request data
        form_data = dict(request.form)
        if id is None:
            if form_data.get("id") is None:
                return generate_response("danger", INVALID_ID, ENDPOINT, 400)
            id = int(form_data.get("id"))
            form_data.pop("id")

        # Check if listener exists
        listener: ListenerModel = Session.query(ListenerModel).filter_by(id=id).first()
        if listener is None:
            return generate_response("danger", LISTENER_DOES_NOT_EXIST, ENDPOINT, 400)

        # Edit listener
        try:
            listener.edit(form_data)
            Session.commit()
        except Exception as e:
            return generate_response("danger", str(e), ENDPOINT, 500)

        LogEntryModel.log(
            "success",
            "listeners",
            f"Edited listener '{listener.name}' ({listener.type})",
            Session,
            get_current_user(),
        )
        return generate_response("success", f"Edited listener with ID {id}.", ENDPOINT)

    @listeners_bp.route("/<int:id>/start", methods=["POST"])
    @authorized
    def post_start(id: int):
        # Check if listener exists
        listener: ListenerModel = Session.query(ListenerModel).filter_by(id=id).first()

        if listener is None:
            return generate_response("danger", LISTENER_DOES_NOT_EXIST, ENDPOINT, 400)

        log(f"({get_current_user().username}) Starting Listener with ID {id}", "info")

        try:
            status = start_listener(listener, commander)
        except Exception as e:
            LogEntryModel.log(
                "danger",
                "listeners",
                status,
                Session,
                get_current_user(),
            )
            return generate_response("danger", str(e), ENDPOINT, 400)
        else:
            LogEntryModel.log(
                "success",
                "listeners",
                status,
                Session,
                get_current_user(),
            )
            return generate_response("success", status, ENDPOINT)

    @listeners_bp.route("/<int:id>/stop", methods=["POST"])
    @authorized
    def post_stop(id: int):
        # Check if listener exists
        listener: ListenerModel = Session.query(ListenerModel).filter_by(id=id).first()

        if listener is None:
            return generate_response("danger", LISTENER_DOES_NOT_EXIST, ENDPOINT, 400)

        log(f"({get_current_user().username}) Stopping Listener with ID {id}", "info")

        try:
            stop_listener(listener, commander)
        except Exception as e:
            return generate_response("danger", str(e), ENDPOINT, 500)
        else:
            LogEntryModel.log(
                "success",
                "listeners",
                f"Stopped listener '{listener.name}' ({listener.type})",
                Session,
                get_current_user(),
            )
            return generate_response(
                "success", f"Stopped Listener with ID {id}", ENDPOINT
            )

    @listeners_bp.route("/<int:id>/restart", methods=["POST"])
    @authorized
    def post_restart(id: int):
        # Check if listener exists
        listener: ListenerModel = Session.query(ListenerModel).filter_by(id=id).first()

        try:
            log(
                f"({get_current_user().username}) restarting listener with ID {id}.",
                "success",
            )
            restart_listener(listener, commander)
        except Exception as e:
            LogEntryModel.log(
                "danger",
                "listeners",
                f"Failed to restart listener '{listener.name}' ({listener.type}): {str(e)}",
                Session,
                get_current_user(),
            )
            return generate_response("danger", str(e), ENDPOINT, 500)
        else:
            LogEntryModel.log(
                "success",
                "listeners",
                f"Restarted listener '{listener.name}' ({listener.type})",
                Session,
                get_current_user(),
            )
            return generate_response(
                "success", f"Restarted listener with ID {id}", ENDPOINT
            )

    return listeners_bp
