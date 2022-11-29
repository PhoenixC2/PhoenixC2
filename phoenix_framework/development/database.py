"""Test Database in the memory"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from phoenix_framework.server.database.base import Base

engine = create_engine("sqlite:///:memory:", echo=True)
Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)