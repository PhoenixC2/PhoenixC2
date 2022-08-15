"""The Listeners Model"""
import json
from sqlalchemy import Column, String, Integer, Text, JSON
from sqlalchemy.orm import relationship
from .base import Base
from .stagers import StagerModel


class ListenerModel(Base):
    """The Listeners Model"""
    __tablename__ = "Listeners"
    listener_id: int = Column(Integer, primary_key=True, nullable=False, name="id")
    name: str = Column(String(100))
    listener_type: str = Column(String(100), name="type")
    config: dict = Column(JSON)
    stagers: list[StagerModel] = relationship("StagerModel")