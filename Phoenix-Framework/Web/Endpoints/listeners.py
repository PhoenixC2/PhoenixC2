from flask import (
    Blueprint,
    render_template,
    jsonify,
    flash,
    redirect,
    session,
    request)
from Utils.ui import log
from Utils.web import generate_response, authorized, get_current_user
from Database import db_session, ListenerModel
from Creator.listener import create_listener, start_listener, stop_listener
from Creator.options import AVAILABLE_LISTENERS


def listeners_bp(server):
    listeners_bp = Blueprint("listeners", __name__, url_prefix="/listeners")

    @listeners_bp.route("/", methods=["GET"])
    @authorized
    def index():
        use_json = request.args.get("json", "").lower() == "true"
        listeners: list[ListenerModel] = db_session.query(ListenerModel).all()
        if use_json:
            return jsonify([listener.to_json(server) for listener in listeners])
        return render_template("listeners.html", listeners)

    @listeners_bp.route("/available", methods=["POST"])
    @authorized
    def available():
        return jsonify(AVAILABLE_LISTENERS)

    @listeners_bp.route("/add", methods=["POST"])
    @authorized
    def post_add():
        """Add a listener
        Request Body Example:
        {
            "type": "socket/reverse/tcp",
            "name": "Test Listener1",
            "address": "10.10.10.10",
            "port": "8080",
            "ssl": "true",
        }
        """
        # Get Form Data
        listener_type = request.form.get("type")
        name = request.form.get("name")
        address = request.form.get("address")
        port = request.form.get("port")
        ssl = request.form.get("ssl").lower() == "true"

        # Check if Data is Valid
        if not listener_type or not name or not address or not port:
            return generate_response("error", "Missing required data.", "listeners", 400)
        if not port.isdigit():
            return generate_response("error", "Invalid Port.", "listeners", 400)
        port = int(port)

        # Create Listener
        try:
            create_listener(listener_type, name, address, int(port), ssl)
        except Exception as e:
            return generate_response("error", str(e), "listeners", 500)

        log(f"({get_current_user().username}) Created Listener {name} ({listener_type}).", "success")
        return generate_response("success", f"Created Listener {name} ({listener_type}).", "listeners")

    @listeners_bp.route("/remove", methods=["DELETE"])
    @authorized
    def delete_remove():
        """Remove a listener
        Request Body Example:
        {
            "id": 1,
        }
        """
        # Get Request Data
        id = request.form.get("id")
        stop = request.form.get("stop", "").lower() == "true"

        if not id.isdigit():
            return generate_response("error", "Invalid ID.", "listeners", 400)
        id = int(id)

        # Check if Listener exists
        listener: ListenerModel = db_session.query(
            ListenerModel).filter_by(listener_id=id).first()
        if listener is None:
            return generate_response("error", "Listener does not exist.", "listeners", 400)

        for stager in listener.stagers:
            db_session.delete(stager)
        db_session.delete(listener)
        db_session.commit()
        if stop:
            if listener.is_active(server):
                stop_listener(id, server)
                log(f"({get_current_user().username}) Deleted and stopped listener with ID {id}.", "info")
                return generate_response("success", f"Deleted and stopped listener with ID {id}.", "listeners")
        
        log(f"({get_current_user().username}) Deleted listener with ID {id}.", "info")
        return generate_response("success", f"Deleted listener with ID {id}.", "listeners")

    @listeners_bp.route("/edit", methods=["PUT"])
    @authorized
    def put_edit():
        """Edit a listener
        Request Body Example:
        {
            "id": "1",
            "change": "name",
            "value": "Test Listener1"
        }
        """
        # Get Request Data
        change = request.form.get("change", "").lower()
        value = request.form.get("value", "")
        id = request.form.get("id", "")

        # Check if Data is Valid
        if not change or not value or not id:
            return generate_response("error", "Missing required data.", "listeners", 400)

        if not id.isdigit():
            return generate_response("error", "Invalid ID.", "listeners", 400)
        id = int(id)

        # Check if Listener exists
        listener: ListenerModel = db_session.query(
            ListenerModel).filter_by(listener_id=id).first()
        
        if listener is None:
            return generate_response("error", "Listener does not exist.", "listeners", 400)

        log(f"({get_current_user().username}) Edited {change} to {value} for Listener with ID {id}.", "success")

        # Change Listener
        if change == "name":
            listener.name = value

        elif change == "address":
            listener.address = value

        elif change == "port":
            listener.port = value

        else:
            return generate_response("error", "Invalid Change.", "listeners", 400)

        db_session.commit()
        return generate_response("success", f"Edited {change} to {value} for Listener with ID {id}.", "listeners")


    @listeners_bp.route("/start", methods=["POST"])
    @authorized
    def post_start():
        """Start a listener
        Request Body Example:
        {
            "id": "1"
        }
        """
        # Get Request Data
        id = request.form.get("id", "")

        if not id.isdigit():
            return generate_response("error", "Invalid ID.", "listeners", 400)
        id = int(id)

        log(f"({get_current_user().username}) Starting Listener with ID {id}", "info")

        try:
            status = start_listener(id, server)
        except Exception as e:
            log(str(e), "error")
            return generate_response("error", str(e), "listeners", 500)
        else:
            log(f"({get_current_user().username}) Started Listener with ID {id}", "success")
            return generate_response("success", status, "listeners")

    @listeners_bp.route("/stop", methods=["POST"])
    @authorized
    def post_stop():
        """Stop a listener
        Request Body Example:
        {
            "id": "1"
        }
        """
        # Get Request Data
        use_json = request.args.get("json", "").lower() == "true"
        id = request.form.get("id", "")

        if not id.isdigit():
            return generate_response("error", "Invalid ID.", "listeners", 400)
        id = int(id)

        # Check if Listener exists
        listener: ListenerModel = db_session.query(
            ListenerModel).filter_by(listener_id=id).first()
        
        if listener is None:
            return generate_response("error", "Listener does not exist.", "listeners", 400)

        log(f"({get_current_user().username}) Stopping Listener with ID {id}", "info")

        try:
            stop_listener(id, server)
        except Exception as e:
            log(f"({get_current_user().username})" + str(e), "error")
            return generate_response("error", str(e), "listeners", 500)
        else:
            log(f"({get_current_user().username}) Stopped Listener with ID {id}", "success")
            return generate_response("success", f"Stopped Listener with ID {id}", "listeners")
    return listeners_bp
