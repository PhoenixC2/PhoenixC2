"""The Users Model"""
from datetime import datetime
from hashlib import md5
from typing import TYPE_CHECKING

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Table, Text)
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .logs import LogEntryModel

user_logentry_association_table = Table(
    "association",
    Base.metadata,
    Column("user_id", ForeignKey("Users.id"), primary_key=True),
    Column("logentry_id", ForeignKey("Logs.id"), primary_key=True),
)


class UserModel(Base):
    """The Users Model"""

    __tablename__ = "Users"
    id: int = Column(Integer, primary_key=True, nullable=False)
    username: str = Column(String(50))
    password: str = Column(Text)
    api_key: str = Column(String(30), nullable=False)
    admin: bool = Column(Boolean)
    last_activity: datetime = Column(DateTime, onupdate=datetime.now)
    disabled: bool = Column(Boolean, default=False)
    profile_picture: str = Column(String(100), default="/static/images/icon.png")
    logs: list["LogEntryModel"] = relationship(
        "LogEntryModel", back_populates="user"
    )  # Logs triggered by user
    unseen_logs: list["LogEntryModel"] = relationship(
        "LogEntryModel",
        secondary=user_logentry_association_table,
        back_populates="unseen_users",
    )  # Logs not seen by user yet

    def set_password(self, password: str):
        """Hash the Password and save it."""
        self.password = md5(password.encode()).hexdigest()

    def check_password(self, password: str):
        """Check if the password is right"""
        return md5(password.encode()).hexdigest() == self.password

    def to_dict(self, show_logs: bool = True, show_unseen_logs: bool = True) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "admin": self.admin,
            "last_activity": self.last_activity,
            "status": self.activity_status,
            "disabled": self.disabled,
            "profile_picture": self.profile_picture,
            "logs": [
                log.to_dict(show_user=False, show_unseen_users=False)
                for log in self.logs
            ]
            if show_logs
            else [log.id for log in self.logs],
            "unseen_logs": [
                log.to_dict(show_unseen_users=True) for log in self.unseen_logs
            ]
            if show_unseen_logs
            else [log.id for log in self.unseen_logs],
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

    def edit(self, data: dict) -> None:
        """Edit the user"""
        self.username = data.get("username", self.username)
        self.admin = data.get("admin", self.admin)
        self.disabled = data.get("disabled", self.disabled)
        self.profile_picture = data.get("profile_picture", self.profile_picture)
        if data.get("password", None) is not None:
            self.set_password(data.get("password", None))
