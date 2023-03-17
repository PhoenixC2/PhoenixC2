"""Test Database in the memory"""
from .testing import change_to_testing_config


def change_to_memory_database():
    """Switch to in-memory database and create tables"""
    change_to_testing_config()
    from phoenixc2.server.database.base import Base
    from phoenixc2.server.database.engine import engine
    from phoenixc2.server.utils.admin import recreate_super_user

    Base.metadata.create_all(engine)
    recreate_super_user()
