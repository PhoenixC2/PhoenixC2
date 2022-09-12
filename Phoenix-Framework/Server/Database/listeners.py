"""The Listeners Model"""
import importlib
import json
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, Column, Integer, String
from sqlalchemy.orm import Session, relationship

from .base import Base

if TYPE_CHECKING:
    from Commander.commander import Commander
    from Listeners.base import BaseListener
    from Utils.options import OptionPool
    from .stagers import StagerModel


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
            "limit": self.connection_limit,
            "active": self.is_active(commander),
            "options": self.options
        }
        if show_stagers:
            data["stagers"] = [stager.to_json(
                commander, False) for stager in self.stagers]
        return data

    def delete_stagers(self, db_session: Session):
        """Delete all stagers if listener is getting removed"""
        for stager in self.stagers:
            db_session.delete(stager)

    def get_listener_object(self, commander: "Commander") -> "BaseListener":
        """Create the Listener Object"""
        return importlib.import_module("Listeners." + self.type.replace("/", ".")).Listener(
            commander, self)

    def get_options(self, commander: "Commander") -> "OptionPool":
        """Return Options based on own listener type"""
        return self.get_listener_object(commander).option_pool

    @staticmethod
    def create_listener_from_data(data: dict):
        standard = []  
        # gets standard values present in every listener and remove them to only leave options
        for st_value in ["name", "type", "address", "port", "ssl", "limit"]:
            standard.append(data.pop(st_value))
        return ListenerModel(
            name=standard[0],
            type=standard[1],
            address=standard[2],
            port=standard[3],
            ssl=standard[4],
            connection_limit=standard[5],
            options=data
        )
