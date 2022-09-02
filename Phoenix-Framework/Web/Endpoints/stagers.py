from flask import (
    Blueprint,
    send_file,
    render_template,
    jsonify,
    flash,
    redirect,
    session,
    request)

from Utils.ui import log
from Utils.web import generate_response, authorized, get_current_user
from Database import db_session, StagerModel
from Creator.stager import get_stager, add_stager
from Creator.options import AVAILABLE_ENCODINGS, AVAILABLE_FORMATS, AVAILABLE_STAGERS

stagers_bp = Blueprint("stagers", __name__, url_prefix="/stagers")


@stagers_bp.route("/", methods=["GET"])
@authorized
def index():
    use_json = request.args.get("json", "") == "true"
    stagers: list[StagerModel] = db_session.query(StagerModel).all()
    if use_json:
        return jsonify([stager.to_json() for stager in stagers])
    return render_template("stagers.html", stagers=stagers)


@stagers_bp.route("/available", methods=["POST"])
@authorized
def available():
    return jsonify(AVAILABLE_STAGERS)


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
    random_size = request.form.get("random_size", "") == "true"
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
            delay
        )
    except Exception as e:
        return generate_response(use_json, "error", str(e), "stagers", 500)
    else:
        log(f"({get_current_user().username}) Created Stager {name}", "success")
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
    stager: StagerModel = db_session.query(
        StagerModel).filter_by(stager_id=id).first()
    if stager is None:
        return generate_response(use_json, "error", "Stager does not exist.", "stagers", 400)

    db_session.delete(stager)
    db_session.commit()

    log(f"({get_current_user().username}) Deleted Stager with ID {id}", "info")
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
    id = request.form.get("id", "")
    change = request.form.get("change", "").lower()
    value = request.form.get("value", "").lower(
    ) if change != "name" else request.form.get("value", "")

    # Check if Data is Valid
    if not change or not value or not id:
        return generate_response(use_json, "error", "Missing required data.", "stagers", 400)
    if not id.isdigit():
        return generate_response(use_json, "error", "Invalid ID.", "stagers", 400)

    # Check if Stager exists
    stager: StagerModel = db_session.query(
        StagerModel).filter_by(stager_id=id).first()
    if stager is None:
        return generate_response(use_json, "error", "Stager does not exist.", "stagers", 400)

    log(f"({get_current_user().username}) Edited {change} to {value} for Stager with ID {id}.", "success")
    # Change Stager
    if change == "encoding" and value in AVAILABLE_ENCODINGS:
        stager.encoding = value
    elif change == "name" and len(value) >= 1:
        stager.name = value
    elif change == "random_size":
        stager.random_size = value == "true"
    elif change == "timeout" and value.isdigit():
        stager.timeout = int(value)
    elif change == "stager_format" or change == "format" and value in AVAILABLE_FORMATS:
        stager.stager_format = value
    elif change == "delay" and value.isdigit():
        stager.delay = int(value)
    else:
        return generate_response(use_json, "error", "Invalid Change.", "stagers", 400)
    db_session.commit()
    return generate_response(use_json, "success", f"Edited {change} to {value} for Stager with ID {id}.", "stagers")


@stagers_bp.route("/download", methods=["GET"])
def get_download():
    """Download a stager
    \nRequest Args Example:
    \nhttp://localhost:8080/stagers/download?id=1&encoding=base64&random_size=True&timeout=5000&format=py&delay=10&finished=true
    """
    # Get Request Data
    use_json = request.args.get("json", "").lower() == "true"
    id = request.args.get("id", "")
    one_liner = request.args.get("one_liner", "") == "true"

    if not id.isdigit():
        return generate_response(use_json, "error", "Invalid ID.", "stagers", 400)
    id = int(id)
    # Check if Stager exists
    stager: StagerModel = db_session.query(
        StagerModel).filter_by(stager_id=id).first()
    if stager is None:
        return generate_response(use_json, "error", "Stager does not exist.", "stagers", 400)

    # Get Stager
    try:
        stager_content = get_stager(id, one_liner)
    except Exception as e:
        return generate_response(use_json, "error", str(e), "stagers", 500)
    else:
        if stager.stager_format == "py":
            return jsonify({"status": "success", "data": stager_content}) if use_json else stager_content
        elif stager.stager_format == "exe":
            with open("/tmp/stager.exe", "wb") as f:
                f.write(stager_content)
            return send_file("/tmp/stager.exe", as_attachment=True, download_name=f"stager.exe")
