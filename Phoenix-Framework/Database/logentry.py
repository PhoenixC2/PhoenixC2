"""The Log Entries Model"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from .base import Base


class LogEntry(Base):
    """The Log Entries Model"""
    __tablename__ = "Logs"
    log_id = Column(Integer, primary_key=True,
                    nullable=False, name="id")
    log_type = Column(String(10), name="type") # info|alert|error|critical|success
    time = Column(DateTime)
    description = Column(Text)



    