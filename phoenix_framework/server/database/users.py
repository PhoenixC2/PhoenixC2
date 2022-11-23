"""The Users Model"""
import json
from uuid import uuid1
import os
from datetime import datetime
from hashlib import md5
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship
from werkzeug.datastructures import FileStorage

from phoenix_framework.server.utils.resources import get_resource

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
    id = Column(Integer, primary_key=True)
    id: int = Column(Integer, primary_key=True, nullable=False)
    username: str = Column(String(50))
    password: str = Column(Text)
    api_key: str = Column(String(30), nullable=False)
    admin: bool = Column(Boolean)
    disabled: bool = Column(Boolean, default=False)
    profile_picture: str = Column(Boolean, default=False)
    logs: list["LogEntryModel"] = relationship(
        "LogEntryModel", back_populates="user"
    )  # Logs triggered by user
    unseen_logs: list["LogEntryModel"] = relationship(
        "LogEntryModel",
        secondary=user_logentry_association_table,
        back_populates="unseen_users",
    )  # Logs not seen by user yet
    last_login = Column(DateTime)
    last_activity: datetime = Column(DateTime, onupdate=datetime.now)

    def set_password(self, password: str):
        """Hash the Password and save it."""
        self.password = md5(password.encode()).hexdigest()

    def check_password(self, password: str):
        """Check if the password is right"""
        return md5(password.encode()).hexdigest() == self.password

    def generate_api_key(self) -> None:
        """Generate a new API Key"""
        self.api_key = str(uuid1())
        
    def to_dict(self, show_logs: bool = True, show_unseen_logs: bool = True) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "admin": self.admin,
            "status": self.activity_status,
            "disabled": self.disabled,
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
            "last_login": self.last_login,
            "last_activity": self.last_activity,
        }

    def to_json(self, show_logs: bool = True, show_unseen_logs: bool = True) -> str:
        return json.dumps(self.to_dict(show_logs, show_unseen_logs), default=str)

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

    def set_profile_picture(self, file: FileStorage) -> None:
        """Set the profile picture and save it"""

        if self.profile_picture:
            os.rm(str(get_resource("data", self.profile_picture, skip_file_check=True)))

        self.profile_picture = True
        file.save(get_resource("data/pictures/", self.username, skip_file_check=True))

    def get_profile_picture(self) -> str:
        """Get the profile picture"""
        return str(get_resource("data/pictures/", self.username)) if self.profile_picture else get_resource("web/static/images", "icon.png")