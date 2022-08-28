"""The Listeners Model"""
import json
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from Server.server_class import ServerClass
from .base import Base
from .stagers import StagerModel


class ListenerModel(Base):
    """The Listeners Model"""
    __tablename__ = "Listeners"
    listener_id: int = Column(Integer, primary_key=True, nullable=False, name="id")
    name: str = Column(String(100))
    listener_type: str = Column(String(100), name="type")
    stagers: list[StagerModel] = relationship("StagerModel")
    address: str = Column(String(15))
    port: int = Column(Integer)
    ssl: bool = Column(Boolean)
    def to_json(self, server:ServerClass) -> dict:
        return {
            "id": self.listener_id,
            "name": self.name,
            "type": self.listener_type,
            "address": self.address,
            "port": self.port,
            "ssl": self.ssl,
            "stagers": [stager.to_json() for stager in self.stagers]
            }