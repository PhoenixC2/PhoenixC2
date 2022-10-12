from Commander import Commander
from Creator.stager import add_stager
from Database import Session, StagerModel
from flask import Blueprint, jsonify, render_template, request, send_file
from Utils.ui import log
from Utils.web import (authorized, generate_response, get_current_user,
                       get_messages)

INVALID_ID = "Invalid ID."
STAGER_DOES_NOT_EXIST = "Stager does not exist."
ENDPOINT = "stagers"

def stagers_bp(commander: Commander):

    stagers_bp = Blueprint(ENDPOINT, __name__, url_prefix="/stagers")

    @stagers_bp.route("/", methods=["GET"])
    @authorized
    def get_stagers():
        use_json = request.args.get("json", "") == "true"
        stager_query = Session.query(StagerModel)
        stagers: list[StagerModel] = stager_query.all()
        if use_json:
            return jsonify([stager.to_dict(commander) for stager in stagers])
        opened_stager = stager_query.filter_by(
            id=request.args.get("open")).first()
        return render_template("stagers.j2", stagers=stagers, opened_stager=opened_stager, messages=get_messages())

    @stagers_bp.route("/options", methods=["GET"])
    @authorized
    def get_options():
        # Get
        stager_type = request.args.get("type")
        try:
            return jsonify(StagerModel.get_options_from_type(stager_type).to_dict(commander))
        except Exception as e:
            return generate_response("danger", str(e), ENDPOINT, 400)

    @stagers_bp.route("/add", methods=["POST"])
    @authorized
    def post_add():
        # Get request data
        use_json = request.args.get("json", "").lower() == "true"
        name = request.form.get("name")
        stager = request.form.get("stager", "")
        data = dict(request.form)
        try:
            # Check if data is valid and clean it
            stager: StagerModel = Session.query(
                StagerModel).filter_by(id=stager).first()
            if stager is None:
                return generate_response("danger", f"stager with ID ({stager}) doesn't exist.", ENDPOINT, 400)
            options = StagerModel.get_options_from_type(stager.type)
            data = options.validate_all(data)
        except Exception as e:
            return generate_response("danger", str(e), ENDPOINT, 400)

        # Add stager
        try:
            stager = add_stager(data)
        except Exception as e:
            return generate_response("danger", str(e), ENDPOINT, 500)

        log(f"({get_current_user().username}) Created Stager '{name}' ({stager.type}).", "success")
        if use_json:
            return jsonify({"status": "success", "stager": stager.to_dict(commander)}), 201
        return generate_response("success", f"Successfully created stager '{name}'.", ENDPOINT)

    @stagers_bp.route("/<int:id>/remove", methods=["DELETE"])
    @authorized
    def delete_remove():
        # Check if Stager exists
        stager: StagerModel = Session.query(
            StagerModel).filter_by(id=id).first()
        if stager is None:
            return generate_response("danger", STAGER_DOES_NOT_EXIST, ENDPOINT, 400)

        Session.delete(stager)
        Session.commit()

        log(f"({get_current_user().username}) Deleted Stager with ID {id}", "info")
        return generate_response("success", f"Deleted Stager with ID {id}.", ENDPOINT)

    @stagers_bp.route("/edit", methods=["PUT", "POST"])
    @stagers_bp.route("/<int:id>/edit", methods=["PUT", "POST"])
    @authorized
    def put_edit(id: int = None):
        # Get request data
        form_data = dict(request.form)
        if id is None:
            if form_data.get("id") is None:
                return generate_response("danger", INVALID_ID, ENDPOINT, 400)
            id = int(form_data.get("id"))
            form_data.pop("id")

        # Check if stager exists
        stager: StagerModel = Session.query(
            StagerModel).filter_by(id=id).first()
        if stager is None:
            return generate_response("danger", STAGER_DOES_NOT_EXIST, ENDPOINT, 400)

        # Edit stager
        try:
            stager.edit(form_data)
            Session.commit()
        except Exception as e:
            return generate_response("danger", str(e), ENDPOINT, 500)
        
        log(f"({get_current_user().username}) Edited stager with ID {id}.", "info")
        return generate_response("success", f"Edited stager with ID {id}.", ENDPOINT)

    @stagers_bp.route("/<int:id>/download", methods=["GET"])
    def get_download():
        # Get Request Data
        use_json = request.args.get("json", "").lower() == "true"
        one_liner = request.args.get("one_liner", "") == "true"

        # Check if Stager exists
        stager_db: StagerModel = Session.query(
            StagerModel).filter_by(id=id).first()
        if stager_db is None:
            return generate_response("danger", STAGER_DOES_NOT_EXIST, ENDPOINT, 400)

        # Get Stager
        try:
            stager_content = get_stager(stager_db, one_liner)
        except Exception as e:
            return generate_response("danger", str(e), ENDPOINT, 500)
        else:
            if stager_db.format == "py":
                return jsonify({"status": "success", "data": stager_content}) if use_json else stager_content
            elif stager_db.format == "exe":
                with open("/tmp/stager.exe", "wb") as f:
                    f.write(stager_content)
                return send_file("/tmp/stager.exe", as_attachment=True, download_name="stager.exe")
    return stagers_bp
