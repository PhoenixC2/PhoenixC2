"""The Stagers Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

if TYPE_CHECKING:
    from .listeners import ListenerModel

class StagerModel(Base):
    """The Stagers Model"""
    __tablename__ = "Stagers"
    id: int = Column(Integer, primary_key=True, nullable=False)
    listener_id: int = Column(Integer, ForeignKey("Listeners.id", ondelete="CASCADE"))
    name: str = Column(String(100))
    listener: "ListenerModel" = relationship("ListenerModel", back_populates="Stagers")
    encoding: str = Column(String(10))
    random_size: bool = Column(Boolean)
    timeout: int = Column(Integer)
    stager_format: str = Column(String(10))
    delay: int = Column(Integer)

    def to_json(self, server) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "listener": self.listener.to_json(server),
            "encoding": self.encoding,
            "random_size": self.random_size,
            "timeout": self.timeout,
            "stager_format": self.stager_format,
            "delay": self.delay
        }