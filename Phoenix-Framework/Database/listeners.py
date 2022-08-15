"""The Listeners Model"""
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship
from .base import Base


class Listener(Base):
    """The Listeners Model"""
    __tablename__ = "Listeners"
    listener_id = Column(Integer, primary_key=True, nullable=False, name="id")
    name = Column(String(100))
    listener_type = Column(String(100), name="type")
    config = Column(Text)
    stagers = relationship("Stager")