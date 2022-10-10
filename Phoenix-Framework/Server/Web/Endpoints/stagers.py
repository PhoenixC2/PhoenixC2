from Commander import Commander
from Creator.available import AVAILABLE_ENCODINGS, AVAILABLE_FORMATS
from Creator.stager import add_stager, get_stager
from Database import ListenerModel, Session, StagerModel
from flask import Blueprint, jsonify, render_template, request, send_file
from Utils.ui import log
from Utils.web import (authorized, generate_response, get_current_user,
                       get_messages)

INVALID_ID = "Invalid ID."
STAGER_DOES_NOT_EXIST = "Stager does not exist."
def stagers_bp(commander: Commander):

    stagers_bp = Blueprint("stagers", __name__, url_prefix="/stagers")

    @stagers_bp.route("/", methods=["GET"])
    @authorized
    def get_stagers():
        use_json = request.args.get("json", "") == "true"
        stager_query = Session.query(StagerModel)
        stagers: list[StagerModel] = stager_query.all()
        if use_json:
            return jsonify([stager.to_dict(commander) for stager in stagers])
        opened_stager = stager_query.filter_by(id=request.args.get("open")).first()
        return render_template("stagers.j2", stagers=stagers, opened_stager=opened_stager, messages=get_messages())

    @stagers_bp.route("/options", methods=["GET"])
    @authorized
    def get_options():
        # Get
        listener_type = request.args.get("type")
        try:
            return jsonify(StagerModel.get_options_from_type(listener_type).to_dict(commander))
        except Exception as e:
            return generate_response("danger", str(e), "listeners", 400)

    @stagers_bp.route("/add", methods=["POST"])
    @authorized
    def post_add():
        # Get request data
        use_json = request.args.get("json", "").lower() == "true"
        name = request.form.get("name")
        listener = request.form.get("listener", "")
        data = dict(request.form)
        try:
            # Check if data is valid and clean it
            listener: ListenerModel = Session.query(ListenerModel).filter_by(id=listener).first()
            if listener is None:
                return generate_response("danger", f"Listener with ID ({listener}) doesn't exist.", "listeners", 400)
            options = StagerModel.get_options_from_type(listener.type)
            data = options.validate_all(data)
        except Exception as e:
            return generate_response("danger", str(e), "listeners", 400)

        # Add listener
        try:
            stager = add_stager(data)
        except Exception as e:
            return generate_response("danger", str(e), "listeners", 500)

        log(f"({get_current_user().username}) Created Stager '{name}' ({listener.type}).", "success")
        if use_json:
            return jsonify({"status": "success", "stager": stager.to_dict(commander)}), 201
        return generate_response("success", f"Successfully created stager '{name}'.", "stagers")

    @stagers_bp.route("/remove", methods=["DELETE"])
    @authorized
    def delete_remove():
        # Get Request Data
        stager_id = request.form.get("id", "")

        if not stager_id.isdigit():
            return generate_response("danger", INVALID_ID, "stagers", 400)

        # Check if Stager exists
        stager: StagerModel = Session.query(
            StagerModel).filter_by(id=stager_id).first()
        if stager is None:
            return generate_response("danger", STAGER_DOES_NOT_EXIST, "stagers", 400)

        Session.delete(stager)
        Session.commit()

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
            return generate_response("danger", "Missing required data.", "stagers", 400)
        if not stager_id.isdigit():
            return generate_response("danger", INVALID_ID, "stagers", 400)

        # Check if Stager exists
        stager: StagerModel = Session.query(
            StagerModel).filter_by(id=stager_id).first()
        if stager is None:
            return generate_response("danger", STAGER_DOES_NOT_EXIST, "stagers", 400)

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
            return generate_response("danger", "Invalid Change.", "stagers", 400)
        Session.commit()
        return generate_response("success", f"Edited {change} to {value} for Stager with ID {stager_id}.", "stagers")

    @stagers_bp.route("/download", methods=["GET"])
    def get_download():
        # Get Request Data
        use_json = request.args.get("json", "").lower() == "true"
        stager_id = request.args.get("id", "")
        one_liner = request.args.get("one_liner", "") == "true"

        if not stager_id.isdigit():
            return generate_response("danger", INVALID_ID, "stagers", 400)
        stager_id = int(stager_id)
        # Check if Stager exists
        stager_db: StagerModel = Session.query(
            StagerModel).filter_by(id=stager_id).first()
        if stager_db is None:
            return generate_response("danger", STAGER_DOES_NOT_EXIST, "stagers", 400)

        # Get Stager
        try:
            stager_content = get_stager(stager_db, one_liner)
        except Exception as e:
            return generate_response("danger", str(e), "stagers", 500)
        else:
            if stager_db.format == "py":
                return jsonify({"status": "success", "data": stager_content}) if use_json else stager_content
            elif stager_db.format == "exe":
                with open("/tmp/stager.exe", "wb") as f:
                    f.write(stager_content)
                return send_file("/tmp/stager.exe", as_attachment=True, download_name="stager.exe")
    return stagers_bp
