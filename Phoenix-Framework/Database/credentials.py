"""The Credentials Model"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text
from .base import Base


class CredentialModel(Base):
    """The Credentials Model"""
    __tablename__ = "Credentials"
    credential_id: int = Column(Integer, primary_key=True, nullable=False, name="id")
    user: str = Column(String(100))
    credential: str = Column(String(100))
    hash: bool = Column(Boolean, default=False)
    found_at: datetime = Column(DateTime)
    notes : str = Column(Text)
    device_id: int = Column(Integer, ForeignKey("Devices.id"))

    def to_json(self) -> dict:
        return {
            "id": self.credential_id,
            "user": self.user,
            "credential": self.credential,
            "found_at": self.found_at,
            "notes": self.notes,
            "device_id": self.device_id,
        }