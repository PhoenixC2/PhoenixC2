"""The Devices Model"""
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship

from .base import Base
from .credentials import CredentialModel

if TYPE_CHECKING:
    from Commander.commander import Commander

class DeviceModel(Base):
    """The Devices Model"""
    __tablename__ = "Devices"
    id: int = Column(Integer, primary_key=True, nullable=False)
    hostname: str = Column(String(100))
    address: str = Column(String(100))
    connection_date: datetime = Column(DateTime)
    last_online: datetime = Column(DateTime)

    def to_json(self, commander: Commander) -> dict:
        data = {
            "id": self.id,
            "hostname": self.hostname,
            "address": self.address,
            "connection_date": self.connection_date,
            "last_online": self.last_online,
        }
        try:
            commander.get_active_handler(self.id)
        except:
            data["online"] = False
        else:
            data["online"] = True
        return data
