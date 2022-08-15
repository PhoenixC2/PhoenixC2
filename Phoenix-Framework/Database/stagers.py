"""The Stagers Model"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from .base import Base


class Stager(Base):
    """The Stagers Model"""
    __tablename__ = "Stagers"
    stager_id = Column(Integer, primary_key=True, nullable=False, name="id")
    name = Column(String(100))
    listener_id = Column(Integer, ForeignKey("Listeners.listener_id"))
    encoder = Column(String(10))
    random_size = Column(Boolean)
    timeout = Column(Integer)
    payload_format = Column(String(10))
    delay = Column(Integer)

    