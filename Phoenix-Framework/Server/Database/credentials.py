"""The Credentials Model"""
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, Integer, String,
                        Text)

from .base import Base


class CredentialModel(Base):
    """The Credentials Model"""
    __tablename__ = "Credentials"
    id: int = Column(Integer, primary_key=True, nullable=False)
    user: str = Column(String(100))
    credential: str = Column(String(100))
    hash: bool = Column(Boolean, default=False)
    found_at: datetime = Column(DateTime)
    notes : str = Column(Text(500))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user": self.user,
            "credential": self.credential,
            "found_at": self.found_at,
            "notes": self.notes,
            "device_id": self.device_id,
        }