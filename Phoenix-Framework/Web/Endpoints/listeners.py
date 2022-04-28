from Utils import *
from Web.Endpoints.authorization import authorized, admin
from Creator import create_listener

listeners = Blueprint("listeners", __name__, url_prefix="/listeners")

@listeners.route("/")
@authorized
def index():
    return render_template("listeners.html")

@listeners.route("/add", methods=["POST"])
@authorized
def post_add():

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
    
    # Get Request Data
    id = request.args.get("id")

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

    # Get Request Data
    change = request.form.get("change")
    id = request.form.get("id")
    
    # Check if Listener exists
    curr.execute("SELECT * FROM Listeners WHERE ID = ?", (id,))
    if curr.fetchone():
        return f"Listener with ID {id} does not exist", 404
    
    # Change Listener
    if change == "name":
        name = request.form.get("name")
        curr.execute("UPDATE Listeners SET Name = ? WHERE ID = ?", (name, id))
        conn.commit()
        return f"Changed Listener with ID {id} to {name}"
    elif change == "address":
        address = request.form.get("address")
        curr.execute("UPDATE Listeners SET Config = ? WHERE ID = ?", (json.dumps({"address": address}), id))
        conn.commit()
        return f"Changed Listener with ID {id} to {address}"
    elif change == "port":
        port = request.form.get("port")
        curr.execute("UPDATE Listeners SET Config = ? WHERE ID = ?", (json.dumps({"port": port}), id))
        conn.commit()
        return f"Changed Listener with ID {id} to {port}"
    else:
        return "Invalid Change", 400