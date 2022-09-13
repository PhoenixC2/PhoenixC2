from Commander.commander import Commander
from Creator.available import AVAILABLE_ENCODINGS, AVAILABLE_FORMATS
from Creator.stager import add_stager, get_stager
from Database import StagerModel, db_session
from flask import Blueprint, jsonify, render_template, request, send_file
from Utils.ui import log
from Utils.web import authorized, generate_response, get_current_user


def stagers_bp(commander: Commander):

    stagers_bp = Blueprint("stagers", __name__, url_prefix="/stagers")

    @stagers_bp.route("/", methods=["GET"])
    @authorized
    def index():
        use_json = request.args.get("json", "") == "true"
        stagers: list[StagerModel] = db_session.query(StagerModel).all()
        if use_json:
            return jsonify([stager.to_json(commander) for stager in stagers])
        return render_template("stagers.html", stagers=stagers)

    @stagers_bp.route("/options", methods=["GET"])
    @authorized
    def get_options():
        # Get
        listener_type = request.args.get("type")
        try:
            return jsonify(StagerModel.get_options_from_type(listener_type).to_json(commander))
        except Exception as e:
            return generate_response("error", str(e), "listeners", 400)

    @stagers_bp.route("/add", methods=["POST"])
    @authorized
    def post_add():
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
            return generate_response("error", "Missing required data.", "stagers", 400)

        if not listener_id.isdigit():
            return generate_response("error", "Invalid ID.", "stagers", 400)
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
            return generate_response("error", str(e), "stagers", 500)
        else:
            log(f"({get_current_user().username}) Created Stager {name}", "success")
            return generate_response("success", f"Added Stager {name}.", "stagers")

    @stagers_bp.route("/remove", methods=["DELETE"])
    @authorized
    def delete_remove():
        # Get Request Data
        stager_id = request.args.get("id", "")

        if not stager_id.isdigit():
            return generate_response("error", "Invalid ID.", "stagers", 400)

        # Check if Stager exists
        stager: StagerModel = db_session.query(
            StagerModel).filter_by(id=stager_id).first()
        if stager is None:
            return generate_response("error", "Stager does not exist.", "stagers", 400)

        db_session.delete(stager)
        db_session.commit()

        log(f"({get_current_user().username}) Deleted Stager with ID {stager_id}", "info")
        return generate_response("success", f"Deleted Stager with ID {stager_id}.", "stagers")

    @stagers_bp.route("/edit", methods=["PUT"])
    @authorized
    def put_edit():
        # Get Request Data
        stager_id = request.args.get("id", "")
        change = request.form.get("change", "").lower()
        value = request.form.get("value", "").lower(
        ) if change != "name" else request.form.get("value", "")

        # Check if Data is Valid
        if not change or not value or not stager_id:
            return generate_response("error", "Missing required data.", "stagers", 400)
        if not stager_id.isdigit():
            return generate_response("error", "Invalid ID.", "stagers", 400)

        # Check if Stager exists
        stager: StagerModel = db_session.query(
            StagerModel).filter_by(id=stager_id).first()
        if stager is None:
            return generate_response("error", "Stager does not exist.", "stagers", 400)

        log(f"({get_current_user().username}) Edited {change} to {value} for Stager with ID {stager_id}.", "success")
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
            stager.format = value
        elif change == "delay" and value.isdigit():
            stager.delay = int(value)
        else:
            return generate_response("error", "Invalid Change.", "stagers", 400)
        db_session.commit()
        return generate_response("success", f"Edited {change} to {value} for Stager with ID {stager_id}.", "stagers")

    @stagers_bp.route("/download", methods=["GET"])
    def get_download():
        # Get Request Data
        use_json = request.args.get("json", "").lower() == "true"
        stager_id = request.args.get("id", "")
        one_liner = request.args.get("one_liner", "") == "true"

        if not stager_id.isdigit():
            return generate_response("error", "Invalid ID.", "stagers", 400)
        stager_id = int(stager_id)
        # Check if Stager exists
        stager_db: StagerModel = db_session.query(
            StagerModel).filter_by(id=stager_id).first()
        if stager_db is None:
            return generate_response("error", "Stager does not exist.", "stagers", 400)

        # Get Stager
        try:
            stager_content = get_stager(stager_db, one_liner)
        except Exception as e:
            return generate_response("error", str(e), "stagers", 500)
        else:
            if stager_db.format == "py":
                return jsonify({"status": "success", "data": stager_content}) if use_json else stager_content
            elif stager_db.format == "exe":
                with open("/tmp/stager.exe", "wb") as f:
                    f.write(stager_content)
                return send_file("/tmp/stager.exe", as_attachment=True, download_name=f"stager.exe")
    return stagers_bp
