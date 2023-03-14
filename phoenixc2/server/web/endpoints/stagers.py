import tempfile

from flask import Blueprint, render_template, request, send_file

from phoenixc2.server.commander import Commander
from phoenixc2.server.database import (
    ListenerModel,
    LogEntryModel,
    Session,
    StagerModel,
    UserModel,
    OperationModel,
)
from phoenixc2.server.utils.misc import Status

INVALID_ID = "Invalid ID."
STAGER_DOES_NOT_EXIST = "Stager does not exist."
ENDPOINT = "stagers"


def stagers_bp(commander: Commander):
    stagers_bp = Blueprint(ENDPOINT, __name__, url_prefix="/stagers")

    @stagers_bp.route("/", methods=["GET"])
    @stagers_bp.route("/<int:stager_id>", methods=["GET"])
    @UserModel.authenticated
    def get_stagers(stager_id: int = None):
        use_json = request.args.get("json", "") == "true"
        show_listener = request.args.get("listener", "") == "true"
        show_stagers = request.args.get("stagers", "") == "true"
        show_all = request.args.get("all", "") == "true"

        opened_stager: StagerModel = (
            Session.query(StagerModel).filter_by(id=stager_id).first()
        )
        if show_all or OperationModel.get_current_operation() is None:
            stagers: list[StagerModel] = Session.query(StagerModel).all()
        else:
            stagers: list[StagerModel] = Session.query(StagerModel).filter(
                StagerModel.operation == OperationModel.get_current_operation()
            )
        stager_types = StagerModel.get_all_classes()
        listeners: list[ListenerModel] = Session.query(ListenerModel).all()

        if use_json:
            if opened_stager is not None:
                return {
                    "status": Status.Success,
                    "stager": opened_stager.to_dict(
                        commander, show_listener, show_stagers
                    ),
                }
            return {
                "status": Status.Success,
                "stagers": [
                    stager.to_dict(commander, show_listener, show_stagers)
                    for stager in stagers
                ],
            }
        return render_template(
            "stagers.j2",
            stagers=stagers,
            opened_stager=opened_stager,
            listeners=listeners,
            stager_types=stager_types,
        )

    @stagers_bp.route("/available", methods=["GET"])
    @UserModel.authenticated
    def get_available():
        stagers = {}
        type = request.args.get("type")
        try:
            if type == "all" or type is None:
                for stager in StagerModel.get_all_classes():
                    stagers[stager.name] = stager.to_dict(commander)
            else:
                stagers[type] = StagerModel.get_class_from_type(type).to_dict(commander)
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400

        else:
            return stagers

    @stagers_bp.route("/add", methods=["POST"])
    @UserModel.authenticated
    def post_add():
        # Get request data
        use_json = request.args.get("json", "").lower() == "true"
        name = request.form.get("name")
        data = dict(request.form)
        try:
            # check if listener exists
            listener: ListenerModel = (
                Session.query(ListenerModel).filter_by(id=data.get("listener")).first()
            )

            if listener is None:
                raise ValueError("Listener does not exist.")

            # check if name is given
            if not name:
                raise ValueError("Name is required.")

            # check if stager name is already taken
            if Session.query(StagerModel).filter_by(name=name).first():
                raise ValueError("Stager name is already taken.")

            # get class for options
            stager_class = StagerModel.get_class_from_type(listener.type)
            option_pool = stager_class.option_pool

            # get payload options
            if "payload" in data and data["payload"] in stager_class.payloads:
                option_pool.extend(stager_class.payloads[data["payload"]].option_pool)

            # Check if data is valid and clean it
            data = option_pool.validate_all(data)

        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400

        # Add stager
        try:
            stager = StagerModel.create_from_data(data)
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400

        Session.add(stager)
        Session.commit()

        LogEntryModel.log(
            Status.Success,
            "stagers",
            f"Created stager '{stager.name}' from Listener '{listener.name}'.",
            UserModel.get_current_user(),
        )
        return (
            (
                {
                    "status": Status.Success,
                    "message": "Stager created successfully.",
                    "stager": stager.to_dict(commander),
                }
            ),
            201,
        )

    @stagers_bp.route("/<int:id>/remove", methods=["DELETE"])
    @UserModel.authenticated
    def delete_remove(id: int):
        # Check if Stager exists
        stager: StagerModel = Session.query(StagerModel).filter_by(id=id).first()

        if stager is None:
            return {"status": Status.Danger, "message": INVALID_ID}, 400

        # set listener name because we need it after the stager is deleted
        listener_name = stager.listener.name

        stager.delete()

        LogEntryModel.log(
            Status.Success,
            "stagers",
            f"Deleted stager '{stager.name}' from Listener '{listener_name}'",
            UserModel.get_current_user(),
        )
        return {"status": Status.Success, "message": "Stager deleted successfully."}

    @stagers_bp.route("/<int:id>/edit", methods=["PUT"])
    @UserModel.authenticated
    def put_edit(id: int = None):
        # Get request data
        form_data = dict(request.form)
        if id is None:
            if form_data.get("id") is None:
                return {"status": Status.Danger, "message": INVALID_ID}, 400
            id = int(form_data.get("id"))
            form_data.pop("id")

        # Check if stager exists
        stager: StagerModel = Session.query(StagerModel).filter_by(id=id).first()
        if stager is None:
            return {"status": Status.Danger, "message": INVALID_ID}, 400

        # Edit stager
        try:
            stager.edit(form_data)
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400

        Session.commit()

        LogEntryModel.log(
            Status.Success,
            "stagers",
            f"Edited stager '{stager.name}'",
            UserModel.get_current_user(),
        )
        return {
            "status": Status.Success,
            "message": "Stager edited successfully.",
            "stager": stager.to_dict(commander),
        }

    @stagers_bp.route("/<int:id>/download", methods=["GET"])
    def get_download(id: int):
        # Get Request Data
        use_json = request.args.get("json", "").lower() == "true"
        one_liner = request.args.get("one_liner", "") == "true"
        recompile = request.args.get("recompile", "") == "true"

        # Check if Stager exists
        stager_db: StagerModel = Session.query(StagerModel).filter_by(id=id).first()
        if stager_db is None:
            return {"status": Status.Danger, "message": INVALID_ID}, 400

        # Get Stager
        try:
            final_payload = stager_db.stager_class.generate(
                stager_db, one_liner, recompile
            )
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400
        else:
            if final_payload.payload.compiled:
                return send_file(
                    final_payload.output,
                    as_attachment=True,
                    download_name=final_payload.name,
                )
            if use_json:
                return {
                    "status": Status.Success,
                    "message": "Stager generated successfully.",
                    "stager": final_payload.output,
                }
            else:
                tmp = tempfile.TemporaryFile()
                tmp.write(final_payload.output.encode())
                tmp.seek(0)
                return send_file(
                    tmp, as_attachment=True, download_name=final_payload.name
                )

    return stagers_bp
