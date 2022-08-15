"""The DevicesModel"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from Utils.libraries import datetime
from .base import Base


class DeviceModel(Base):
    """The Devices Model"""
    __tablename__ = "Devices"
    device_id: int = Column(Integer, primary_key=True, nullable=False, name="id")
    hostname: str = Column(String(100))
    address: str = Column(String(100))
    connection_date: datetime = Column(DateTime)
    last_online: datetime = Column(DateTime)
