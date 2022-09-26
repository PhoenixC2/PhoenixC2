"""The Users Model"""
from datetime import datetime
from hashlib import md5
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from .base import Base

if TYPE_CHECKING:
    from .logentries import LogEntryModel

class UserModel(Base):
    """The Users Model"""
    __tablename__ = "Users"
    id: int = Column(Integer, primary_key=True, nullable=False)
    username: str = Column(String(50))
    password: str = Column(Text)
    api_key: str = Column(String(30), nullable=False)
    admin: bool = Column(Boolean)
    last_activity: datetime = Column(DateTime)
    disabled: bool = Column(Boolean, default=False)
    profile_picture: str = Column(String(100), default="/static/images/icon.png")
    logs: list["LogEntryModel"] = relationship(
        "LogEntryModel",
        back_populates="user")
    def set_password(self, password:str):
        """Hash the Password and save it."""
        self.password = md5(password.encode()).hexdigest()
    
    def check_password(self, password:str):
        """Check if the password is right"""
        return md5(password.encode()).hexdigest() == self.password
    
    def to_json(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "admin": self.admin,
            "last_activity": self.last_activity,
            "status": self.activity_status,
            "disabled": self.disabled,
            "profile_picture": self.profile_picture
        }
    def __str__(self) -> str:
        return self.username
    
    @property
    def activity_status(self) -> str:
        """Returns the activity based on the last request timestamp"""
        if self.last_activity is None:
            return "offline"
        delta = (datetime.now() - self.last_activity).seconds / 60
        if delta <= 5:
            return "online"
        elif delta <= 20:
            return "inactive"
        else:
            return "offline"