"""The Listeners Model"""
import json
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from .base import Base
from .stagers import StagerModel

if TYPE_CHECKING:
    from Server.server_class import ServerClass


class ListenerModel(Base):
    """The Listeners Model"""
    __tablename__ = "Listeners"
    listener_id: int = Column(
        Integer, primary_key=True, nullable=False, name="id")
    name: str = Column(String(100))
    listener_type: str = Column(String(100), name="type")
    stagers: list[StagerModel] = relationship("StagerModel")
    address: str = Column(String(15))
    port: int = Column(Integer)
    ssl: bool = Column(Boolean)
    connection_limit = Column(Integer, name="limit")

    def is_active(self, server):
        """Returns True if listeners is active, else False"""
        try:
            server.get_active_listener(self.listener_id)
        except:
            return False
        else:
            return True

    def to_json(self, server: "ServerClass") -> dict:
        return {
            "id": self.listener_id,
            "name": self.name,
            "type": self.listener_type,
            "address": self.address,
            "port": self.port,
            "ssl": self.ssl,
            "active": self.is_active(server),
            "stagers": [stager.to_json() for stager in self.stagers]
        }