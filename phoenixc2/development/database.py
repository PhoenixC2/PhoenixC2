"""Test Database in the memory"""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from phoenixc2.server.database.base import Base


def create_memory_database() -> tuple[Engine, Session]:
    """Create a database in memory and return the engine and session"""
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)

    session_factory = sessionmaker(bind=engine)
    return engine, scoped_session(session_factory)
