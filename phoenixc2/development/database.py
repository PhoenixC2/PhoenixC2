"""Test Database in the memory"""
from .testing import change_to_testing_config
from typing import TYPE_CHECKING
from phoenixc2.server.utils.misc import generate_name

if TYPE_CHECKING:
    from phoenixc2.server.database import ListenerModel, StagerModel


def change_to_memory_database():
    """Switch to in-memory database and create tables"""
    change_to_testing_config()
    from phoenixc2.server.database.base import Base
    from phoenixc2.server.database.engine import engine
    from phoenixc2.server.utils.admin import recreate_super_user

    Base.metadata.create_all(engine)
    recreate_super_user()


def generate_listener(
    name: str = generate_name(),
    type: str = "http-reverse",
    options: dict = {},
) -> "ListenerModel":
    """Generate a mock listener based on the http-reverse kit by default

    Args:
    -----
        name: The name of the listener
        type: The type of the listener
        options: The options for the listener

    Returns:
    --------
        ListenerModel: The listener model
    """
    from phoenixc2.server.database import ListenerModel, Session

    options["name"] = name
    options = ListenerModel.get_class_from_type(
        "http-reverse"
    ).option_pool.validate_all(options)
    options["type"] = type
    listener = ListenerModel.create_from_data(options)
    Session.add(listener)
    return listener


def generate_stager(
    name: str = generate_name(),
    listener: "ListenerModel" = None,
    options: dict = {},
) -> "StagerModel":
    """Generate a mock stager based on the http kit by default

    Args:
    -----
        name: The name of the stager
        type: The type of the stager
        options: The options for the stager

    Returns:
    --------
        StagerModel: The stager model
    """
    from phoenixc2.server.database import StagerModel, Session

    if listener is None:
        listener = generate_listener()
    options["name"] = name
    options["listener"] = listener.name
    options = StagerModel.get_class_from_type("http-reverse").option_pool.validate_all(
        options
    )
    stager = StagerModel.create_from_data(options)
    Session.add(stager)
    Session.add(listener)
    return stager
