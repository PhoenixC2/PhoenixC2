"""The Log Entries Model"""
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .users import UserModel
class LogEntryModel(Base):
    """The Log Entries Model"""
    __tablename__ = "Logs"
    id: int = Column(Integer, primary_key=True,
                    nullable=False)
    alert: str = Column(String(10), name="type") # info|alert|error|critical|success
    time: datetime = Column(DateTime)
    description: str = Column(Text(100))
    user_id: int = Column(Integer, ForeignKey("Users.id"))
    user: "UserModel" = relationship(
        "UserModel", back_populates="logs"
    )
    def to_json(self) -> dict:
        return {
            "id": self.id,
            "type": self.alert,
            "time": self.time,
            "description": self.description
        }
    @staticmethod
    def generate_log(alert: str, description: str, user: "UserModel" = None) -> "LogEntryModel":
        return LogEntryModel(
            alert=alert,
            time=datetime.now(),
            description=description,
            user=user
        )