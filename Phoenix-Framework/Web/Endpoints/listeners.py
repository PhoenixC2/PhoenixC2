from Utils import *
from Web.Endpoints.authorization import authorized, admin
from Creator import create_listener, start_listener, stop_listener

def listeners_endpoints(server):
    listeners = Blueprint("listeners", __name__, url_prefix="/listeners")

    @listeners.route("/", methods=["GET"])
    @authorized
    def index():
        return render_template("listeners.html")

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
        listener_type = request.form.get("type")
        name = request.form.get("name")
        address = request.form.get("address")
        port = request.form.get("port")
        ssl = request.form.get("ssl")

        # Create Listener
        try:
            create_listener(listener_type, name, address, int(port), ssl)
        except Exception as e:
            return str(e)
        return f"Listener {name} created"

    @listeners.route("/remove", methods=["DELETE"])
    @authorized
    def delete_remove():
        """Remove a listener
        \nRequest Args Example:
        \nhttp://localhost:5000/listeners/remove?id=1
        """
        # Get Request Data
        id = request.args.get("id")
        try:
            id = int(id)
        except ValueError:
            return "Invalid ID", 400

        # Check if Listener exists
        curr.execute("SELECT * FROM Listeners WHERE ID = ?", (id,))
        if not curr.fetchone():
            return f"Listener with ID {id} does not exist", 404
        curr.execute("DELETE FROM Listeners WHERE ID = ?", (id,))
        conn.commit()
        return f"Removed Listener with ID {id}"

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
        id = request.form.get("id")
        try:
            id = int(id)
        except ValueError:
            return "Invalid ID", 400
        change = request.form.get("change")
        value = request.form.get("value")
        # Check if Listener exists
        curr.execute("SELECT * FROM Listeners WHERE ID = ?", (id,))
        if curr.fetchone():
            return f"Listener with ID {id} does not exist", 404
        
        # Change Listener
        if change == "name":
            curr.execute("UPDATE Listeners SET Name = ? WHERE ID = ?", (value, id))
            conn.commit()
            return f"Changed Listener with ID {id} to {value}"
        elif change == "address":
            curr.execute("UPDATE Listeners SET Config = ? WHERE ID = ?", (json.dumps({"address": value}), id))
            conn.commit()
            return f"Changed Listener with ID {id} to {value}"
        elif change == "port":
            curr.execute("UPDATE Listeners SET Config = ? WHERE ID = ?", (json.dumps({"port": value}), id))
            conn.commit()
            return f"Changed Listener with ID {id} to {value}"
        else:
            return "Invalid Change", 400

    @listeners.route("/list", methods=["GET"])
    @authorized
    def get_list():
        # improve this
        curr.execute("SELECT * FROM Listeners")
        listnrs = curr.fetchall()
        data = []
        for i, l in enumerate(listnrs):
            try:
                active = server.get_listener(l[0])
            except:
                active = False
            else:
                active = True
            data[i] = {
                "id": l[0],
                "name": l[1],
                "type": l[2],
                "config": json.loads(l[3]),
                "active": active
            }
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
        id = request.form.get("id")
        try:
            id = int(id)
        except ValueError:
            return "Invalid ID", 400
        
        # Check if Listener exists
        curr.execute("SELECT * FROM Listeners WHERE ID = ?", (id,))
        listener = curr.fetchone()
        if not listener:
            return f"Listener with ID {id} does not exist", 404
        
        try:
            start_listener(id, server)
        except Exception as e:
            return str(e), 500
        else:
            return f"Started Listener with ID {id}"
    
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
        id = request.form.get("id")
        try:
            id = int(id)
        except ValueError:
            return "Invalid ID", 400
        
        # Check if Listener exists
        curr.execute("SELECT * FROM Listeners WHERE ID = ?", (id,))
        listener = curr.fetchone()
        if not listener:
            return f"Listener with ID {id} does not exist", 404
        
        try:
            stop_listener(id)
        except Exception as e:
            return str(e), 500
        else:
            return f"Stopped Listener with ID {id}"
    return listeners