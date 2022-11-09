"""Create Stagers to download or copy"""
from phoenix_framework.server.database import Session, StagerModel


def add_stager(data: dict) -> StagerModel:
    """
    Add a stager to the database
    """

    # Check if name is already in use
    name = data["name"]
    if Session.query(StagerModel).filter_by(name=name).first() is not None:
        raise ValueError(f"Stager {name} already exists")

    stager = StagerModel.create_stager_from_data(data)
    Session.add(stager)
    Session.commit()
    return stager
