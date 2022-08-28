"""The Users Model"""
from datetime import datetime
from hashlib import md5
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from .base import Base


class UserModel(Base):
    """The Users Model"""
    __tablename__ = "Users"
    user_id: int = Column(Integer, primary_key=True, nullable=False, name="id")
    username: str = Column(String(50))
    password: str = Column(Text)
    admin: bool = Column(Boolean)
    last_online: datetime = Column(DateTime)
    disabled: bool = Column(Boolean, default=False)
    profile_picture: str = Column(String(100), default="/static/images/icon.png")

    def set_password(self, password:str):
        """Hash the Password and save it."""
        self.password = md5(password.encode()).hexdigest()
    
    def check_password(self, password:str):
        """Check if the password is right"""
        return md5(password.encode()).hexdigest() == self.password
    
    def to_json(self) -> dict:
        return {
            "id": self.user_id,
            "username": self.username,
            "admin": self.admin,
            "last_online": self.last_online,
            "disabled": self.disabled,
            "profile_picture": self.profile_picture
        }