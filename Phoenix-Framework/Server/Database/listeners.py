"""The Listeners Model"""
import json
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Integer, Boolean, JSON
from sqlalchemy.orm import relationship, Session
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
    type: str = Column(String(100))
    stagers: list["StagerModel"] = relationship(
        "StagerModel",
        back_populates="listener")
    address: str = Column(String(15))
    port: int = Column(Integer)
    ssl: bool = Column(Boolean)
    connection_limit = Column(Integer, name="limit")
    options: dict = Column(JSON, default=[])

    def is_active(self, commander: "Commander"):
        """Returns True if listeners is active, else False"""
        try:
            commander.get_active_listener(self.id)
        except:
            return False
        else:
            return True

    def to_json(self, commander: "Commander", show_stagers: bool = True) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "address": self.address,
            "port": self.port,
            "ssl": self.ssl,
            "active": self.is_active(commander),
            "options": self.options
        }
        if show_stagers:
            data["stagers"] = [stager.to_json(commander, False) for stager in self.stagers]
        return data
    
    def delete_stagers(self, db_session: Session):
        """Delete all stagers if listener is getting removed"""
        for stager in self.stagers:
            db_session.delete(stager)
