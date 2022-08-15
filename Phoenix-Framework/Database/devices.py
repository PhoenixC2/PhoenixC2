"""The DevicesModel"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from .base import Base


class Device(Base):
    """The Devices Model"""
    __tablename__ = "Devices"
    device_id = Column(Integer, primary_key=True, nullable=False, name="id")
    hostname = Column(String(100))
    address = Column(String(100))
    connection_date = Column(DateTime)
    last_online = Column(DateTime)
