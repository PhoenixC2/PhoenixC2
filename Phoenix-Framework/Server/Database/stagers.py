"""The Stagers Model"""
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from Commander.commander import Commander

    from .listeners import ListenerModel

class StagerModel(Base):
    """The Stagers Model"""
    __tablename__ = "Stagers"
    id: int = Column(Integer, primary_key=True, nullable=False)
    name: str = Column(String(100))
    listener_id: int = Column(Integer, ForeignKey("Listeners.id"))
    listener: "ListenerModel" = relationship("ListenerModel", back_populates="stagers")
    encoding: str = Column(String(10))
    random_size: bool = Column(Boolean)
    timeout: int = Column(Integer)
    format: str = Column(String(10))
    delay: int = Column(Integer)

    def to_json(self, commander: "Commander", show_listener: bool = True) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "encoding": self.encoding,
            "random_size": self.random_size,
            "timeout": self.timeout,
            "stager_format": self.format,
            "delay": self.delay
        }
        if show_listener:
            data["listener"] = self.listener.to_json(commander, False)
        return data