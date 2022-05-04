from Utils import *
from Web.Endpoints.authorization import authorized, admin
from Creator import get_stager, create_stager

stagers = Blueprint("stagers", __name__, url_prefix="/stagers")

#TODO: Overthink Creation of Stagers and how to access the finished stager
@stagers.route("/")
@authorized
def index():
    return render_template("stagers.html")


@stagers.route("/add", methods=["POST"])
@authorized
def post_add():
    """Add a stager
    Request Body Example:
    {
        "listener": "1",
        "name": "Test Stager1"
    }
    """
    # Get Form Data
    listener_id = request.form.get("listener")
    name = request.form.get("name")
    # Create Stager
    try:
        create_stager(name, listener_id)
    except Exception as e:
        return str(e)
    else:
        return f"Stager {name} created"


@stagers.route("/remove", methods=["DELETE"])
@authorized
def delete_remove():
    """Remove a stager
    \nRequest Args Example:
    \nhttp://localhost:8080/stagers/remove?id=1
    """

    # Get Request Data
    id = request.args.get("id")
    try:
        id = int(id)
    except ValueError:
        return "Invalid ID", 400
    
    # Check if Stager exists
    curr.execute("SELECT * FROM Stagers WHERE ID = ?", (id,))
    if not curr.fetchone():
        return f"Stager with ID {id} does not exist", 404
    curr.execute("DELETE FROM Stagers WHERE ID = ?", (id,))
    conn.commit()
    return f"Removed Stager with ID {id}"


@stagers.route("/edit", methods=["PUT"])
@authorized
def put_edit():
    """Edit a stager
    Request Body Example:
    {
        "id": "1",
        "changed": "name",
        "value": "Test Stager1"
    }"""

    # Get Request Data
    change = request.form.get("change")
    id = request.form.get("id")
    try:
        id = int(id)
    except ValueError:
        return "Invalid ID", 400
    
    

    value = request.form.get("value")

    # Check if Stager exists
    curr.execute("SELECT * FROM Stagers WHERE ID = ?", (id,))
    if curr.fetchone():
        return f"Stager with ID {id} does not exist", 404

    # Change Stager
    if change == "name":
        curr.execute("UPDATE Stagers SET Name = ? WHERE ID = ?", (value, id))
        conn.commit()
        return f"Changed Stager with ID {id} to {value}"
    else:
        return f"Invalid Change", 400

@stagers.route("/download", methods=["GET"])
@authorized
def post_download():
    """Download a stager
    Request Body Example:
    {
        "id": "1"
        "encoding": "base64"
        "random_size": "True"
        "timeout": 5
        "format": "exe"
        "delay": 5
    }
    """
    # Get Request Data
    id = request.body.get("id")
    encoding = request.body.get("encoding")
    random_size = request.body.get("random_size")
    timeout = request.body.get("timeout")
    format = request.body.get("format")
    delay = request.body.get("delay")
    try:
        id = int(id)
    except ValueError:
        return "Invalid ID", 400
    
    


    # Check if Stager exists
    curr.execute("SELECT * FROM Stagers WHERE ID = ?", (id,))
    if not curr.fetchone():
        return f"Stager with ID {id} does not exist", 404

    # Get Stager
    try:
        stager = get_stager(id, encoding, random_size, timeout, format, delay)
    except Exception as e:
        return str(e), 400
    else:
        return send_file(stager, as_attachment=True, download_name=f"Stager.{format}")