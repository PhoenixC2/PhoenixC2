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

    def to_json(self) -> dict:
        return {
            "id": self.device_id,
            "hostname": self.hostname,
            "address": self.address,
            "connection_date": self.connection_date,
            "last_online": self.last_online
        }