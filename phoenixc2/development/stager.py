from phoenixc2.server.database import StagerModel, Session
from phoenixc2.server.kits.base_payload import FinalPayload


def get_finished_payload(stager: StagerModel, recompile: bool = False) -> FinalPayload:
    """Get the finished payload from the database"""
    stager = Session.query(StagerModel).first()
    return stager.generate_payload(recompile=recompile)


def save_payload_to_file(final_payload: FinalPayload, path: str) -> None:
    """Save the finished payload to a file"""

    if final_payload.payload.compiled:
        with open(path, "wb") as file:
            file.write(final_payload.output)
    else:
        with open(path, "w") as file:
            file.write(final_payload.output)
