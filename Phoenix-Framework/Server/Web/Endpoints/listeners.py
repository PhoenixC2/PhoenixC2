from Commander import Commander
from Creator.listener import (add_listener, restart_listener, start_listener,
                              stop_listener)
from Database import ListenerModel, Session
from flask import Blueprint, jsonify, request, flash
from Utils.misc import get_network_interfaces
from Utils.ui import log
from Utils.web import (authorized, generate_response, get_current_user,
                       render_template)

INVALID_ID = "Invalid ID."
LISTENER_DOES_NOT_EXIST = "Listener does not exist."
def listeners_bp(commander: Commander):
    listeners_bp = Blueprint("listeners", __name__, url_prefix="/listeners")
    @listeners_bp.route("/", methods=["GET"])
    @authorized
    def get_listeners():
        use_json = request.args.get("json", "").lower() == "true"
        listener_query = Session.query(ListenerModel)
        listener_options = ListenerModel.get_all_options(commander)
        listeners: list[ListenerModel] = listener_query.all()
        if use_json:
            return jsonify([listener.to_json(commander) for listener in listeners])
        opened_listener = listener_query.filter_by(
            id=request.args.get("open")).first()
        return render_template("listeners.j2", listeners=listeners, opened_listener=opened_listener, commander=commander, listener_options=listener_options, network_interfaces=get_network_interfaces())

    @listeners_bp.route("/options", methods=["GET"])
    @authorized
    def get_options():
        # Get
        listener_type = request.args.get("type")
        try:
            return jsonify(ListenerModel.get_options_from_type(listener_type).to_json(commander))
        except Exception as e:
            return generate_response("danger", str(e), "listeners", 400)

    @listeners_bp.route("/add", methods=["POST"])
    @authorized
    def post_add():
        # Get request data
        listener_type = request.form.get("type")
        name = request.form.get("name")
        is_interface = request.args.get("is_interface", "").lower() == "true"
        data = dict(request.form)
        if is_interface:
            interfaces = get_network_interfaces()
            if data.get("address", "") in interfaces:
                data["address"] = interfaces[data["address"]]
            else:
                return generate_response("danger", "Invalid network interface.", "listeners", 400)
        try:
            # Check if data is valid and clean it
            options = ListenerModel.get_options_from_type(listener_type)
            data = options.validate_data(data)
        except Exception as e:
            return generate_response("danger", str(e), "listeners", 400)

        # Add listener
        try:
            # has to be added again bc it got filtered out by options.validate_data(data)
            data["type"] = listener_type
            add_listener(data)
        except Exception as e:
            return generate_response("danger", str(e), "listeners", 500)

        log(f"({get_current_user().username}) Created Listener {name} ({listener_type}).", "success")
        return generate_response("success", f"Created Listener {name}' ({listener_type}).", "listeners", 201)

    @listeners_bp.route("/<int:id>/remove", methods=["DELETE"])
    @authorized
    def delete_remove(id : int):
        # Get request data
        stop = request.form.get("stop", "").lower() == "true"

        # Check if listener exists
        listener: ListenerModel = Session.query(
            ListenerModel).filter_by(id=id).first()
        if listener is None:
            return generate_response("danger", LISTENER_DOES_NOT_EXIST, "listeners", 400)

        if stop and listener.is_active(commander):
                stop_listener(listener, commander)
                log(f"({get_current_user().username}) Deleted and stopped listener with ID {id}.", "info")
                return generate_response("success", f"Deleted and stopped listener with ID {id}.", "listeners")
        listener.delete_stagers(Session)
        Session.delete(listener)
        Session.commit()
        log(f"({get_current_user().username}) Deleted listener with ID {id}.", "info")
        return generate_response("success", f"Deleted listener with ID {id}.", "listeners")

    @listeners_bp.route("/<int:id>/edit", methods=["PUT"])
    @authorized
    def put_edit(id : int):
        # Get request data
        change = request.form.get("change", "").lower()
        value = request.form.get("value", "")
        # Check if data is valid
        if not change or not value or not id:
            return generate_response("danger", "Missing required data.", "listeners", 400)


        # Check if listener exists
        listener: ListenerModel = Session.query(
            ListenerModel).filter_by(id=id).first()

        if listener is None:
            return generate_response("danger", LISTENER_DOES_NOT_EXIST, "listeners", 400)

        log(f"({get_current_user().username}) Edited {change} to {value} for Listener with ID {id}.", "success")

        # Change Listener
        if change == "name":
            listener.name = value

        elif change == "address":
            listener.address = value

        elif change == "port":
            listener.port = value

        else:
            return generate_response("danger", "Invalid Change.", "listeners", 400)

        Session.commit()
        return generate_response("success", f"Edited {change} to {value} for Listener with ID {id}.", "listeners")

    @listeners_bp.route("/<int:id>/start", methods=["POST"])
    @authorized
    def post_start(id : int):
        # Check if listener exists
        listener: ListenerModel = Session.query(
            ListenerModel).filter_by(id=id).first()

        if listener is None:
            return generate_response("danger", LISTENER_DOES_NOT_EXIST, "listeners", 400)

        log(f"({get_current_user().username}) Starting Listener with ID {id}", "info")

        try:
            status = start_listener(listener, commander)
        except Exception as e:
            log(f"({get_current_user().username}) {e}", "info")
            return generate_response("danger", str(e), "listeners", 400)
        else:
            log(f"({get_current_user().username}) Started Listener with ID {id}", "success")
            return generate_response("success", status, "listeners")

    @listeners_bp.route("/<int:id>/stop", methods=["POST"])
    @authorized
    def post_stop(id : int):
        # Check if listener exists
        listener: ListenerModel = Session.query(
            ListenerModel).filter_by(id=id).first()

        if listener is None:
            return generate_response("danger", LISTENER_DOES_NOT_EXIST, "listeners", 400)

        log(f"({get_current_user().username}) Stopping Listener with ID {id}", "info")

        try:
            stop_listener(listener, commander)
        except Exception as e:
            return generate_response("danger", str(e), "listeners", 500)
        else:
            log(f"({get_current_user().username}) Stopped Listener with ID {id}", "success")
            return generate_response("success", f"Stopped Listener with ID {id}", "listeners")

    @listeners_bp.route("/<int:id>/restart", methods=["POST"])
    @authorized
    def post_restart(id : int):

        # Check if listener exists
        listener: ListenerModel = Session.query(
            ListenerModel).filter_by(id=id).first()

        try:
            log(f"({get_current_user().username}) restarting listener with ID {id}.", "success")
            restart_listener(listener, commander)
        except Exception as e:
            log(f"({get_current_user().username}) failed to restart listener with ID {id}.", "success")
            return generate_response("danger", str(e), "listeners", 500)
        else:
            log(f"({get_current_user().username}) restarted listener with ID {id}.", "success")
            return generate_response("success", f"Restarted listener with ID {id}", "listeners")
    return listeners_bp
