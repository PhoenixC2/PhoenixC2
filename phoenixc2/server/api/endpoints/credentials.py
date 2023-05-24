from flask import Blueprint, request

from phoenixc2.server.database import (
    CredentialModel,
    Session,
    UserModel,
    OperationModel,
    LogEntryModel,
)
from phoenixc2.server.utils.misc import Status

ENDPOINT = "credentials"
credentials_bp = Blueprint(ENDPOINT, __name__, url_prefix="/credentials")


@credentials_bp.route("/", methods=["GET"])
@credentials_bp.route("/<int:cred_id>", methods=["GET"])
@UserModel.authenticated
def get_credentials(cred_id: int = None):
    show_operation = request.args.get("operation", "").lower() == "true"
    show_all = request.args.get("all", "").lower() == "true"

    if cred_id == "all" or cred_id is None:
        if show_all or OperationModel.get_current_operation() is None:
            credentials: list[CredentialModel] = Session.query(CredentialModel).all()
        else:
            credentials: list[CredentialModel] = (
                Session.query(CredentialModel)
                .filter_by(operation=OperationModel.get_current_operation())
                .all()
            )
        return {
            "status": Status.Success,
            "credentials": [
                credential.to_dict(show_operation=show_operation)
                for credential in credentials
            ],
        }
    else:
        credential = Session.query(CredentialModel).filter_by(id=cred_id).first()
        if credential is None:
            return {
                "status": Status.Danger,
                "message": "Credential does not exist",
                "credential": None,
            }
        return {
            "status": Status.Success,
            "credential": credential.to_dict(show_operation=show_operation),
        }


@credentials_bp.route("/add", methods=["POST"])
@UserModel.authenticated
def add_credential():
    value = request.json.get("value", "")
    hash = request.json.get("hash", False)
    user = request.json.get("user", "")
    admin = request.json.get("admin", False)
    try:
        credential = CredentialModel.create(value, hash, user, admin)
    except ValueError as e:
        return {"status": Status.Danger, "message": str(e)}
    Session.add(credential)
    Session.commit()
    LogEntryModel.log(
        Status.Success,
        "credentials",
        "Added credential to the database",
        UserModel.get_current_user(),
    )
    return {
        "status": Status.Success,
        "message": "Credential added Successfully",
        "credential": credential.to_dict(),
    }


@credentials_bp.route("/<int:cred_id>/remove", methods=["DELETE"])
@UserModel.authenticated
def remove_credential(cred_id: int):
    credential: CredentialModel = (
        Session.query(CredentialModel).filter_by(id=cred_id).first()
    )
    if credential is None:
        return {
            "status": "danger",
            "message": "Credential does not exist",
        }

    Session.delete(credential)
    Session.commit()
    LogEntryModel.log(
        Status.Success,
        "credentials",
        "Removed credential from the database",
        UserModel.get_current_user(),
    )
    return {"status": Status.Success, "message": "Credential removed Successfully"}


@credentials_bp.route("/<int:cred_id>/edit", methods=["PUT"])
@UserModel.authenticated
def edit_credential(cred_id: int):
    credential = Session.query(CredentialModel).filter_by(id=cred_id).first()

    if credential is None:
        return {
            "status": "danger",
            "message": "Credential does not exist",
        }, 400
    try:
        credential.edit(request.json)
    except ValueError as e:
        return {"status": Status.Danger, "message": str(e)}
    Session.commit()
    LogEntryModel.log(
        Status.Success,
        "credentials",
        "Edited credential in the database",
        UserModel.get_current_user(),
    )

    return {
        "status": Status.Success,
        "message": "Credential edited Successfully",
        "credential": credential.to_dict(),
    }
