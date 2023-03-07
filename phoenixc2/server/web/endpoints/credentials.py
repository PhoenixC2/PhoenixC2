from flask import Blueprint, jsonify,render_template, request

from phoenixc2.server.database import CredentialModel, Session, UserModel, OperationModel
from phoenixc2.server.utils.web import generate_response

ENDPOINT = "logs"
logs_bp = Blueprint(ENDPOINT, __name__, url_prefix="/logs")


@logs_bp.route("/", methods=["GET"])
@logs_bp.route("/<int:log_id>", methods=["GET"])
@UserModel.authenticated
def get_logs(log_id: int = None):
    use_json = request.args.get("json", "").lower() == "true"
    show_operation = request.args.get("operation", "").lower() == "true"
    show_all = request.args.get("all", "").lower() == "true"

    opened_credential: CredentialModel = (
        Session.query(CredentialModel).filter_by(id=log_id).first()
    )

    if show_all or OperationModel.get_current_operation() is None:
        credentials: list[CredentialModel] = Session.query(CredentialModel).all()
        
    else:
        credentials: list[CredentialModel] = (
            Session.query(CredentialModel)
            .filter_by(operation=OperationModel.get_current_operation())
            .all()
        )

    if use_json:
        if opened_credential is not None:
            return jsonify(
                {
                    "status": "success",
                    "credential": opened_credential.to_dict(
                        show_operation=show_operation
                    ),
                }
            )
        return jsonify(
            {
                "status": "success",
                ENDPOINT: [
            credential.to_dict(show_operation=show_operation)
            for credential in credentials
                ],
            }
        )
    return render_template(
        "credentials.j2",
        credentials=credentials,
        opened_credential=opened_credential,
    )

