from Utils import *
from Web.Endpoints.authorization import authorized, admin
from Creator import create_stager

stagers = Blueprint("stagers", __name__, url_prefix="/stagers")

#TODO: Overthink Creation of Stagers and how to access the finished stager
@stagers.route("/")
@authorized
def index():
    return render_template("stagers.html")


@stagers.route("/add", methods=["POST"])
@authorized
def post_add():

    # Get Form Data
    listener_type = request.form.get("listener")
    encoder = request.form.get("encoder")
    random_size = request.form.get("random_size")
    timeout = request.form.get("timeout")
    exisiting_stager = request.form.get("exisiting_stager")
    name = request.form.get("name")
    format = request.form.get("format")
    delay = request.form.get("delay")
    # Create Stager
    try:
        create_stager(listener_type, encoder, random_size=="True", int(timeout), exisiting_stager, name, format, int(delay))
    except Exception as e:
        return str(e)
    return f"Stager {name} created"


@stagers.route("/remove", methods=["DELETE"])
@authorized
def delete_remove():

    # Get Request Data
    id = request.args.get("id")

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

    # Get Request Data
    change = request.form.get("change")
    id = request.form.get("id")

    # Check if Stager exists
    curr.execute("SELECT * FROM Stagers WHERE ID = ?", (id,))
    if curr.fetchone():
        return f"Stager with ID {id} does not exist", 404

    # Change Stager
    if change == "name":
        name = request.form.get("name")
        curr.execute("UPDATE Stagers SET Name = ? WHERE ID = ?", (name, id))
        conn.commit()
        return f"Changed Stager with ID {id} to {name}"
    elif change == "format":
        format = request.form.get("format")
        curr.execute(
            "UPDATE Stagers SET Format = ? WHERE ID = ?", (format, id))
        conn.commit()
        return f"Changed Stager with ID {id} to {format}"
    elif change == "delay":
        delay = request.form.get("delay")
        curr.execute("UPDATE Stagers SET Delay = ? WHERE ID = ?", (delay, id))
        conn.commit()
        return f"Changed Stager with ID {id} to {delay}"
