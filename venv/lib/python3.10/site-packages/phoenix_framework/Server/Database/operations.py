"""The Log Entries Model"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from .base import Base


#TODO Add Association Table for many to many relationship between operations and users|devices|credentials
class OperationModel(Base):
    """The Operation Model"""
    __tablename__ = "Operations"
    log_id: int = Column(Integer, primary_key=True,
                    nullable=False)
    log_type: str = Column(String(10), name="type") # info|alert|error|critical|success
    time: datetime = Column(DateTime)
    description: str = Column(Text)

    def to_dict(self) -> dict:
        return {
            "id": self.log_id,
            "type": self.log_type,
            "time": self.time,
            "description": self.description
        }

    