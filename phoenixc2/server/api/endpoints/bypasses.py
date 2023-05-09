from flask import Blueprint, request, send_file
from phoenixc2.server.commander.commander import Commander
from phoenixc2.server.utils.misc import Status
from phoenixc2.server.database import BypassChainModel, StagerModel, Session
from phoenixc2.server.bypasses import get_all_bypasses, get_bypass


def bypasses_bp(commander: "Commander"):
    bypasses_bp = Blueprint("bypasses", __name__, url_prefix="/bypasses")

    @bypasses_bp.route("/")
    @bypasses_bp.route("/<string:category>/<string:name>")
    def get_bypasses(category: str = None, name: str = None):
        full = request.args.get("full", "").lower() == "true"

        bypasses = get_all_bypasses()
        if category is None and name is None:
            if full:
                full_bypasses = {}
                for category, contained_bypasses in bypasses.items():
                    full_bypasses[category] = [
                        get_bypass(category, name).to_dict(commander)
                        for name in contained_bypasses
                    ]
                return {
                    "status": Status.Success,
                    "bypasses": full_bypasses,
                }
            return {
                "status": Status.Success,
                "bypasses": bypasses,
            }
        else:
            try:
                bypass = get_bypass(category, name)
            except ModuleNotFoundError:
                return {"status": Status.Danger, "message": "Bypass not found."}, 400
        return {"status": Status.Success, "bypass": bypass.to_dict(commander)}

    @bypasses_bp.route("/run/<string:category>/<string:name>", methods=["GET"])
    def get_run_single_bypass(category: str, name: str):
        stager_id = request.args.get("stager", None)

        try:
            bypass = get_bypass(category, name)
        except ModuleNotFoundError:
            return {"status": Status.Danger, "message": "Bypass not found."}, 400

        if stager_id:
            stager: StagerModel = (
                Session.query(StagerModel).filter_by(id=stager_id).first()
            )
            if stager is None:
                return {"status": Status.Danger, "message": "Stager not found."}, 400

        else:
            return {"status": Status.Danger, "message": "No stager provided."}, 400

        try:
            final_payload = stager.generate_payload()
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400

        try:
            bypass.execute(final_payload)
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400

        return send_file(
            final_payload.as_file,
            as_attachment=True,
            download_name=final_payload.name,
        )

    @bypasses_bp.route("/chains")
    @bypasses_bp.route("/chains/<int:chain_id>")
    def get_chains(chain_id: int = None):
        if chain_id is None:
            chains: list[BypassChainModel] = Session.query(BypassChainModel).all()
            return {
                "status": Status.Success,
                "chains": [chain.to_dict(commander) for chain in chains],
            }
        else:
            chain = Session.query(BypassChainModel).filter_by(id=chain_id).first()
            if chain is None:
                return {"status": Status.Danger, "message": "Chain not found."}, 400
            return {"status": Status.Success, "chain": chain.to_dict(commander)}

    @bypasses_bp.route("/chains/add", methods=["POST"])
    def post_add_chain():
        chain = BypassChainModel.create(request.json)
        Session.add(chain)
        Session.commit()
        return {
            "status": Status.Success,
            "message": "Chain added successfully.",
            "chain": chain.to_dict(commander),
        }, 201

    @bypasses_bp.route("/chains/<int:chain_id>/remove", methods=["DELETE"])
    def delete_chain(chain_id: int):
        chain = Session.query(BypassChainModel).filter_by(id=chain_id).first()

        if chain is None:
            return {"status": Status.Danger, "message": "Chain not found."}, 400

        Session.delete(chain)
        Session.commit()
        return {"status": Status.Success, "message": "Chain removed successfully."}, 200

    @bypasses_bp.route("/chains/<int:chain_id>/edit", methods=["PUT"])
    def post_edit_chain(chain_id: int):
        chain = Session.query(BypassChainModel).filter_by(id=chain_id).first()

        if chain is None:
            return {"status": Status.Danger, "message": "Chain not found."}, 400

        chain.edit(request.json)
        Session.commit()
        return {
            "status": Status.Success,
            "message": "Chain updated successfully.",
            "chain": chain.to_dict(commander),
        }, 200

    @bypasses_bp.route("/chains/<int:chain_id>/bypass/add", methods=["POST"])
    def post_add_bypass_to_chain(chain_id: int):
        data = dict(request.json)
        name = data.pop("name", "")
        category = data.pop("category", "")

        chain: BypassChainModel = (
            Session.query(BypassChainModel).filter_by(id=chain_id).first()
        )

        if chain is None:
            return {"status": Status.Danger, "message": "Chain not found."}, 400
        try:
            bypass = get_bypass(category, name)
        except ModuleNotFoundError:
            return {"status": Status.Danger, "message": "Bypass not found."}, 400

        try:
            data = bypass.option_pool.validate_all(data)
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400

        chain.add_bypass(category, name, data)
        Session.commit()

        return {
            "status": Status.Success,
            "message": "Bypass added successfully.",
            "chain": chain.to_dict(commander),
        }, 201

    @bypasses_bp.route(
        "/chains/<int:chain_id>/bypass/<int:bypass_id>/remove/", methods=["DELETE"]
    )
    def delete_bypass_from_chain(chain_id: int, bypass_id: int):
        chain: BypassChainModel = (
            Session.query(BypassChainModel).filter_by(id=chain_id).first()
        )

        if chain is None:
            return {"status": Status.Danger, "message": "Chain not found."}, 400
        try:
            chain.remove_bypass(bypass_id - 1)
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400
        Session.commit()

        return {
            "status": Status.Success,
            "message": "Bypass removed successfully.",
            "chain": chain.to_dict(commander),
        }, 200

    @bypasses_bp.route(
        "/chains/<int:chain_id>/bypass/<int:bypass_id>/move", methods=["PUT"]
    )
    def put_move_bypass_in_chain(chain_id: int, bypass_id: int):
        new_position = request.json.get("position", None)

        if new_position is None:
            return {
                "status": Status.Danger,
                "message": "New position not specified.",
            }, 400

        if not isinstance(new_position, int) and not new_position.isdigit():
            return {
                "status": Status.Danger,
                "message": "New position must be a number.",
            }, 400

        new_position = int(new_position)

        chain: BypassChainModel = (
            Session.query(BypassChainModel).filter_by(id=chain_id).first()
        )

        if chain is None:
            return {"status": Status.Danger, "message": "Chain not found."}, 400
        try:
            chain.move_bypass(bypass_id - 1, new_position - 1)
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400
        Session.commit()

        return {
            "status": Status.Success,
            "message": "Bypass moved successfully.",
            "chain": chain.to_dict(commander),
        }, 200

    @bypasses_bp.route("/chains/<int:chain_id>/run", methods=["GET"])
    def get_run_chain(chain_id: int):
        stager_id = request.args.get("stager", None)

        chain: BypassChainModel = (
            Session.query(BypassChainModel).filter_by(id=chain_id).first()
        )

        if chain is None:
            return {"status": Status.Danger, "message": "Chain not found."}, 400

        stager: StagerModel = Session.query(StagerModel).filter_by(id=stager_id).first()

        if stager is None:
            return {"status": Status.Danger, "message": "Stager not found."}, 400
        try:
            final_payload = stager.generate_payload()
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400

        try:
            final_payload = chain.execute(final_payload)
        except Exception as e:
            return {"status": Status.Danger, "message": str(e)}, 400

        if final_payload.payload.compiled:
            return send_file(
                final_payload.as_file,
                as_attachment=True,
                download_name=final_payload.name,
            )
        return {
            "status": Status.Success,
            "message": "Stager generated successfully.",
            "stager": final_payload.output,
        }

    return bypasses_bp
