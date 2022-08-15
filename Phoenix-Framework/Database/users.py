"""The Users Model"""
from Utils import md5
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from .base import Base


class User(Base):
    """The Users Model"""
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True, nullable=False, name="id")
    username = Column(String(50))
    password = Column(Text)
    admin = Column(Boolean)
    online = Column(Boolean)
    last_online = Column(DateTime)

    def set_password(self, password:str):
        """Hash the Password and save it."""
        self.password = md5(password.encode()).hexdigest()
    
    def check_password(self, password:str):
        """Check if the password is right"""
        return md5(password.encode()).hexdigest() == self.password