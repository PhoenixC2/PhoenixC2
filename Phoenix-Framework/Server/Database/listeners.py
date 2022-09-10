"""The Listeners Model"""
import json
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from .base import Base

if TYPE_CHECKING:
    from .stagers import StagerModel
    from Commander.commander import Commander


class ListenerModel(Base):
    """The Listeners Model"""
    __tablename__ = "Listeners"
    id: int = Column(
        Integer, primary_key=True, nullable=False)
    name: str = Column(String(100))
    listener_type: str = Column(String(100), name="type")
    stagers: list[StagerModel] = relationship(
        "StagerModel",
        back_populates="Listeners",
        cascade="all, delete",
        passive_deletes=True)
    address: str = Column(String(15))
    port: int = Column(Integer)
    ssl: bool = Column(Boolean)
    connection_limit = Column(Integer, name="limit")

    def is_active(self, commander: "Commander"):
        """Returns True if listeners is active, else False"""
        try:
            commander.get_active_listener(self.id)
        except:
            return False
        else:
            return True

    def to_json(self, commander: "Commander") -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.listener_type,
            "address": self.address,
            "port": self.port,
            "ssl": self.ssl,
            "active": self.is_active(commander),
            "stagers": [stager.to_json() for stager in self.stagers]
        }
