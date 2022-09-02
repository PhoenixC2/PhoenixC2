"""The Devices Model"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from .credentials import CredentialModel


class DeviceModel(Base):
    """The Devices Model"""
    __tablename__ = "Devices"
    device_id: int = Column(Integer, primary_key=True, nullable=False, name="id")
    hostname: str = Column(String(100))
    address: str = Column(String(100))
    connection_date: datetime = Column(DateTime)
    last_online: datetime = Column(DateTime)
    stagers: list[CredentialModel] = relationship("CredentialModel")

    def to_json(self, server=None) -> dict:
        data = {
            "id": self.device_id,
            "hostname": self.hostname,
            "address": self.address,
            "connection_date": self.connection_date,
            "last_online": self.last_online,
        }
        try: 
            server.get_active_handler(self.device_id)
        except:
            data["online"] = False
        else:
            data["online"] = True
        return data