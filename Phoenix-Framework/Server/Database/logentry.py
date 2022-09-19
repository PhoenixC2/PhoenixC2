"""The Log Entries Model"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from .base import Base


class LogEntryModel(Base):
    """The Log Entries Model"""
    __tablename__ = "Logs"
    id: int = Column(Integer, primary_key=True,
                    nullable=False)
    type: str = Column(String(10), name="type") # info|alert|error|critical|success
    time: datetime = Column(DateTime)
    description: str = Column(Text(100))
    

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "time": self.time,
            "description": self.description
        }

    