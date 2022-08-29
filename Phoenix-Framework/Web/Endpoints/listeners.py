from flask import (
    Blueprint,
    render_template,
    jsonify,
    flash,
    redirect,
    session,
    request)
from Utils.ui import log
from Database import db_session, ListenerModel
from Web.Endpoints.authorization import authorized, get_current_user
from Creator.listener import create_listener, start_listener, stop_listener
from Creator.options import listeners as available_listeners


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
        return jsonify(available_listeners)

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
        use_json = request.args.get("json", "").lower() == "true"
        listener_type = request.form.get("type")
        name = request.form.get("name")
        address = request.form.get("address")
        port = request.form.get("port")
        ssl = request.form.get("ssl").lower() == "true"

        # Check if Data is Valid
        if not listener_type or not name or not address or not port:
            if use_json:
                return jsonify({"status": "error", "message": "Missing required data."}), 400
            flash("Missing required data.", "error")
            return redirect("/listeners")

        if not port.isdigit():
            if use_json:
                return jsonify({"status": "error", "message": "Invalid port."}), 400
            flash("Invalid port.", "error")
            return redirect("/listeners")
        port = int(port)
        

        # Create Listener
        try:
            create_listener(listener_type, name, address, int(port), ssl)
        except Exception as e:
            if use_json:
                return jsonify({"status": "error", "message": str(e)}), 400
            flash(str(e), "error")
            return redirect("/listeners")
        
        log(f"({get_current_user(session['id']).username}) Created Listener {name} ({listener_type}).", "success")
        
        if use_json:
            return jsonify({"status": "success", "message": f"Created Listener {name} ({listener_type})."})
        flash("Created Listener.", "success")
        return redirect("/listeners")


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
        use_json = request.args.get("json", "").lower() == "true"
        id = request.form.get("id")

        if not id.isdigit():
            if use_json:
                return jsonify({"status": "error", "message": "Invalid ID"}), 400
            flash("Invalid ID.", "error")
            return redirect("/listeners")
        id = int(id)
            

        # Check if Listener exists
        listener = db_session.query(ListenerModel).filter_by(listener_id=id)
        if listener is None:
            if not use_json:
                flash("Listener does not exist.", "error")
                return redirect("/listeners")
            return jsonify({"status": "error", "message": "Listener does not exist"}), 404
        db_session.delete(listener)
        db_session.commit()
        log(f"({get_current_user(session['id']).username}) Deleted Listener with ID {id}.", "info")
        if not use_json:
            flash(f"Deleted Listener with ID {id}.", "success")
            return redirect("/listeners")
        return jsonify({"status": "success", "message": f"Deleted Listener with ID {id}"})

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
        use_json = request.args.get("json", "").lower() == "true"
        change = request.form.get("change")
        value = request.form.get("value")
        id = request.form.get("id")

        # Check if Data is Valid
        if not change or not value or not id:
            if not use_json:
                flash("Missing required data.", "error")
                return redirect("/listeners")
            return jsonify({"status": "error", "message": "Missing required data"}), 400

        if not id.isdigit():
            if not use_json:
                flash("Invalid ID.", "error")
                return redirect("/listeners")
            return jsonify({"status": "error", "message": "Invalid ID"}), 400
        id = int(id)
        # Check if Listener exists
        listener: ListenerModel = db_session.query(
            ListenerModel).filter_by(listener_id=id).first()
        if listener is None:
            if not use_json:
                flash("Listener does not exist.", "error")
                return redirect("/listeners")
            return jsonify({"status": "error", "message": "Listener does not exist."}), 404

        log(f"({get_current_user(session['id']).username}) Edited {change} to {value} for Listener with ID {id}.", "success")

        # Change Listener
        if change == "name":
            listener.name = value

        elif change == "address":
            listener.address = value

        elif change == "port":
            listener.port = value

        else:
            if use_json:
                return jsonify({"status": "error", "message": "Invalid change."}), 400
            flash("Invalid change.", "error")
            return redirect("/listeners")
        db_session.commit()
        if use_json:
            return jsonify({"status": "success", "message": f"Edited {change} to {value} for Listener with ID {id}."})
        flash(f"Edited Listener with ID {id}.", "success")
        return redirect("/listeners")

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
        use_json = request.args.get("json", "").lower() == "true"
        id= request.form.get("id")
        if not id.isdigit():
            if use_json:
                return jsonify({"status": "error", "message": "Invalid ID"}), 400
            flash("Invalid ID.", "error")
            return redirect("/listeners")
        id = int(id)
        log(f"({get_current_user(session['id']).username}) Starting Listener with ID {id}", "info")

        try:
            status = start_listener(id, server)
        except Exception as e:
            log(str(e), "error")
            if use_json:
                return jsonify({"status": "error", "message": str(e)}), 500
            flash(str(e), "error")
            return redirect("/listeners")
        else:
            log(f"({get_current_user(session['id']).username}) Started Listener with ID {id}", "success")
            if use_json:
                return jsonify({"status": "success", "message": status})
            flash(f"Started Listener with ID {id}", "success")
            return redirect("/listeners")

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
        id = request.form.get("id")

        if not id.isdigit():
            if use_json:
                return jsonify({"status": "error", "message": "Invalid ID."}), 400
            flash("Invalid ID.", "error")
            return redirect("/listeners")

        # Check if Listener exists
        listener: ListenerModel = db_session.query(
            ListenerModel).filter_by(listener_id=id).first()
        if listener is None:
            if not use_json:
                return jsonify({"status": "error", "message": "Listener does not exist."}), 404
            flash("Listener does not exist.", "error")
            return redirect("/listeners")

        log(f"({get_current_user(session['id']).username}) Stopping Listener with ID {id}", "info")

        try:
            stop_listener(id, server)
        except Exception as e:
            log(f"({get_current_user(session['id']).username})" + str(e), "error")
            if use_json:
                return jsonify({"status": "error", "message": f"Failed to stop Listener with ID {id}."}), 500
            flash(f"Failed to stop Listener with ID {id}.", "error")
            return redirect("/listeners")
        else:
            log(f"({get_current_user(session['id']).username}) Stopped Listener with ID {id}", "success")
            if use_json:
                return jsonify({"status": "success", "message": f"Stopped Listener with ID {id}"})
            flash(f"Stopped Listener with ID {id}", "success")
            return redirect("/listeners")
    return listeners_bp
