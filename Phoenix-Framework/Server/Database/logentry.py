"""The Log Entries Model"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from .base import Base


class LogEntryModel(Base):
    """The Log Entries Model"""
    __tablename__ = "Logs"
    log_id: int = Column(Integer, primary_key=True,
                    nullable=False, name="id")
    log_type: str = Column(String(10), name="type") # info|alert|error|critical|success
    time: datetime = Column(DateTime)
    description: str = Column(Text)

    def to_json(self) -> dict:
        return {
            "id": self.log_id,
            "type": self.log_type,
            "time": self.time,
            "description": self.description
        }

    