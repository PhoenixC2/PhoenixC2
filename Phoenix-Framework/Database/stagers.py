"""The Stagers Model"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from .base import Base


class StagerModel(Base):
    """The Stagers Model"""
    __tablename__ = "Stagers"
    stager_id: int = Column(Integer, primary_key=True, nullable=False, name="id")
    name: str = Column(String(100))
    listener_id: int = Column(Integer, ForeignKey("Listeners.listener_id"))
    encoder: str = Column(String(10))
    random_size: bool = Column(Boolean)
    timeout: int = Column(Integer)
    payload_format: str = Column(String(10))
    delay: int = Column(Integer)

    def to_json(self) -> dict:
        return {
            "id": self.stager_id,
            "name": self.name,
            "listener_id": self.listener_id,
            "encoder": self.encoder,
            "random_size": self.random_size,
            "timeout": self.timeout,
            "payload_format": self.payload_format,
            "delay": self.delay
        }