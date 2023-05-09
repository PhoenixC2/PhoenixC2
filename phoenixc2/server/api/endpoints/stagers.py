from flask import Blueprint, request, send_file
from copy import deepcopy
from phoenixc2.server.commander.commander import Commander
from phoenixc2.server.database import (
    ListenerModel,
    LogEntryModel,
    OperationModel,
    Session,
    StagerModel,
    UserModel,
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

        if opened_stager is not None:
            return {
                "status": Status.Success,
                "stager": opened_stager.to_dict(commander, show_listener, show_stagers),
            }
        return {
            "status": Status.Success,
            "stagers": [
                stager.to_dict(commander, show_listener, show_stagers)
                for stager in stagers
            ],
        }

    @stagers_bp.route("/available", methods=["GET"])
    @UserModel.authenticated
    def get_available():
        types = {}
        type = request.args.get("type", "all")
        try:
            if type == "all":
                for stager in StagerModel.get_all_classes():
                    types[stager.name] = stager.to_dict(commander)
            else:
                types[type] = StagerModel.get_class_from_type(type).to_dict(commander)
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400
        else:
            return {
                "status": Status.Success,
                "available": types,
            }

    @stagers_bp.route("/add", methods=["POST"])
    @UserModel.authenticated
    def post_add():
        # Get request data
        name = request.json.get("name")
        data = dict(request.json)

        # check if listener exists
        listener: ListenerModel = (
            Session.query(ListenerModel).filter_by(id=data.get("listener")).first()
        )

        if listener is None:
            return {"status": Status.Danger, "message": "Listener does not exist."}, 400

        # check if name is given
        if not name:
            return {"status": Status.Danger, "message": "Name is required."}, 400

        # check if stager name is already taken
        if Session.query(StagerModel).filter_by(name=name).first():
            return {"status": Status.Danger, "message": "Name is already taken."}, 400

        # get class for options
        stager_class = StagerModel.get_class_from_type(listener.type)
        # so we don't modify the original option pool
        option_pool = deepcopy(stager_class.option_pool)

        # get payload options
        if "payload" in data and data["payload"] in stager_class.payloads:
            option_pool.extend(stager_class.payloads[data["payload"]].option_pool)
        else:
            return {"status": Status.Danger, "message": "Invalid payload."}, 400
        try:
            data = option_pool.validate_all(data)
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400

        # Add stager
        stager = StagerModel.create_from_data(data)

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
        form_data = dict(request.json)
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
        recompile = request.args.get("recompile", "") == "true"

        # Check if Stager exists
        stager_db: StagerModel = Session.query(StagerModel).filter_by(id=id).first()
        if stager_db is None:
            return {"status": Status.Danger, "message": INVALID_ID}, 400

        # Get Stager
        try:
            final_payload = stager_db.generate_payload(recompile)
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400
        else:
            return send_file(
                final_payload.as_file,
                as_attachment=True,
                download_name=final_payload.name,
            )

    return stagers_bp
