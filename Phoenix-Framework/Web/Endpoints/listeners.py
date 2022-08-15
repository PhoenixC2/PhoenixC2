from Utils import *
from Web.Endpoints.authorization import authorized, admin
from Creator.listener import create_listener, start_listener, stop_listener
import Creator.options

def listeners_endpoints(server):
    listeners = Blueprint("listeners", __name__, url_prefix="/listeners")

    @listeners.route("/", methods=["GET"])
    @authorized
    def index():
        return render_template("listeners.html")
    @listeners.route("/available", methods=["POST"])
    @authorized
    def available():
        return jsonify(Creator.options.listeners)
    @listeners.route("/add", methods=["POST"])
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
        use_json = request.args.get("json") == "true"
        listener_type = request.form.get("type")
        name = request.form.get("name")
        address = request.form.get("address")
        port = request.form.get("port")
        ssl = True if request.form.get("ssl").lower() == "true" else False

        # Check if Data is Valid
        if not listener_type or not name or not address or not port:
            return jsonify({"status": "error", "message": "Missing required data"}), 400 if use_json else abort(400, "Missing required data")
        try:
            port = int(port)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid port"}), 400 if use_json else abort(400, "Invalid port")
        # Create Listener
        try:
            create_listener(listener_type, name, address, int(port), ssl)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400 if use_json else abort(400, str(e))
        log(f"({session['username']}) Created Listener {name} ({listener_type})", "success")
        return jsonify({"status": "success", "message": f"Created Listener {name} ({listener_type})"}) if use_json else "Created Listener"

    @listeners.route("/remove", methods=["DELETE"])
    @authorized
    def delete_remove():
        """Remove a listener
        Request Body Example:
        {
            "id": 1,
        }
        """
        # Get Request Data
        use_json = request.args.get("json") == "true"
        id = request.form.get("id")
        try:
            id = int(id)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid ID"}), 400 if use_json else abort(400, "Invalid ID")

        # Check if Listener exists
        curr.execute("SELECT * FROM Listeners WHERE ID = ?", (id,))
        if not curr.fetchone():
            return jsonify({"status": "error", "message": "Listener does not exist"}), 404 if use_json else abort(404, "Listener does not exist")
        curr.execute("DELETE FROM Listeners WHERE ID = ?", (id,))
        conn.commit()
        log(f"({session['username']}) Deleted Listener with ID {id}", "info")
        return jsonify({"status": "success", "message": f"Deleted Listener with ID {id}"}) if use_json else f"Deleted Listener with ID {id}"

    @listeners.route("/edit", methods=["PUT"])
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
        use_json = request.args.get("json") == "true"
        change = request.form.get("change")
        value = request.form.get("value")
        id = request.form.get("id")

        # Check if Data is Valid
        if not change or not value or not id:
            return jsonify({"status": "error", "message": "Missing required data"}), 400 if use_json else abort(400, "Missing required data")

        try:
            id = int(id)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid ID"}), 400 if use_json else abort(400, "Invalid ID")
        # Check if Listener exists
        curr.execute("SELECT * FROM Listeners WHERE ID = ?", (id,))
        if not curr.fetchone():
            return jsonify({"status": "error", "message": "Listener does not exist"}), 404 if use_json else abort(404, "Listener does not exist")

        log(f"({session['username']}) Edited {change} to {value} for Listener with ID {id}", "sucess")
        # Change Listener
        if change == "name":
            curr.execute(
                "UPDATE Listeners SET Name = ? WHERE ID = ?", (value, id))
            conn.commit()
            return jsonify({"status": "success", "message": f"Edited {change} to {value} for Listener with ID {id}"}) if use_json else f"Edited Listener with ID {id}"
        elif change == "address":
            curr.execute("UPDATE Listeners SET Config = ? WHERE ID = ?",
                         (json.dumps({"address": value}), id))
            conn.commit()
            return jsonify({"status": "success", "message": f"Edited {change} to {value} for Listener with ID {id}"}) if use_json else f"Edited Listener with ID {id}"
        elif change == "port":
            curr.execute("UPDATE Listeners SET Config = ? WHERE ID = ?",
                         (json.dumps({"port": value}), id))
            conn.commit()
            return jsonify({"status": "success", "message": f"Edited {change} to {value} for Listener with ID {id}"}) if use_json else f"Edited Listener with ID {id}"
        else:
            return jsonify({"status": "error", "message": "Invalid change"}), 400 if use_json else abort(400, "Invalid change")

    @listeners.route("/list", methods=["GET"])
    @authorized
    def get_list():
        # improve this
        curr.execute("SELECT * FROM Listeners")
        listnrs = curr.fetchall()
        data = []
        for index, l in enumerate(listnrs):
            try:
                active = server.get_listener(index + 1)
            except:
                active = False
            else:
                active = True
            data.append({
                "id": l[0],
                "name": l[1],
                "type": l[2],
                "config": json.loads(l[3]),
                "active": active
            })
        return jsonify(data)

    @listeners.route("/start", methods=["POST"])
    @authorized
    def post_start():
        """Start a listener
        Request Body Example:
        {
            "id": "1"
        }
        """
        # Get Request Data
        use_json = request.args.get("json") == "true"
        id = request.form.get("id")
        try:
            id = int(id)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid ID"}), 400 if use_json else abort(400, "Invalid ID")

        log(f"({session['username']}) Starting Listener with ID {id}", "info")
        try:
            status = start_listener(id, server)
        except Exception as e:
            log(str(e), "error")
            return jsonify({"status": "error", "message": str(e)}), 500 if use_json else abort(500, str(e))
        else:
            log(f"({session['username']}) Started Listener with ID {id}", "success")
            return jsonify({"status": "success", "message": status}) if use_json else f"Started Listener with ID {id}"

    @listeners.route("/stop", methods=["POST"])
    @authorized
    def post_stop():
        """Stop a listener
        Request Body Example:
        {
            "id": "1"
        }
        """
        # Get Request Data
        use_json = request.args.get("json") == "true"
        id = request.form.get("id")
        try:
            id = int(id)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid ID"}), 400

        # Check if Listener exists
        curr.execute("SELECT * FROM Listeners WHERE ID = ?", (id,))
        listener = curr.fetchone()
        if not listener:
            return jsonify({"status": "error", "message": "Listener does not exist"}), 404 if use_json else abort(404, "Listener does not exist")

        log(f"({session['username']}) Stopping Listener with ID {id}", "info")
        try:
            stop_listener(id, server)
        except Exception as e:
            log(f"({session['username']})" + str(e), "error")
            return jsonify({"status": "error", "message": f"Failed to stop Listener with ID {id}"}), 500 if use_json else abort(500, f"Failed to stop Listener with ID {id}")
        else:
            log(f"({session['username']}) Stopped Listener with ID {id}", "success")
            return jsonify({"status": "success", "message": f"Stopped Listener with ID {id}"}) if use_json else f"Stopped Listener with ID {id}"
    return listeners
