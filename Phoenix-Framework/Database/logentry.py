"""The Log Entries Model"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from Utils.libraries import datetime
from .base import Base


class LogEntryModel(Base):
    """The Log Entries Model"""
    __tablename__ = "Logs"
    log_id: int = Column(Integer, primary_key=True,
                    nullable=False, name="id")
    log_type: str = Column(String(10), name="type") # info|alert|error|critical|success
    time: datetime = Column(DateTime)
    description: str = Column(Text)



    