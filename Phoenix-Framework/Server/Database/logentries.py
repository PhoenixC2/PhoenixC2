"""The Log Entries Model"""
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base
from .users import user_logentry_association_table

if TYPE_CHECKING:
    from .users import UserModel


class LogEntryModel(Base):
    """The Log Entries Model"""
    __tablename__ = "Logs"
    id: int = Column(Integer, primary_key=True,
                     nullable=False)
    # info|alert|error|critical|success
    alert: str = Column(String(10), name="type")
    time: datetime = Column(DateTime)
    description: str = Column(Text(100))
    user_id: int = Column(Integer, ForeignKey("Users.id"))
    user: "UserModel" = relationship(
        "UserModel", back_populates="logs"
    )  # user who triggered the log creation
    unseen_users: list["UserModel"] = relationship(
        "UserModel",
        secondary=user_logentry_association_table,
        back_populates="unseen_logs")  # users who haven't seen this message

    def to_json(self, show_user: bool = True, show_unseen_users: bool = True) -> dict:
        return {
            "id": self.id,
            "type": self.alert,
            "time": self.time,
            "description": self.description,
            "user": self.user.to_json(show_logs=False, show_unseen_logs=False)
            if self.user is not None and show_user
            else self.user.id if self.user is not None else None,
            "unseen_users": [user.to_json(show_logs=False, show_unseen_logs=False) for user in self.unseen_users] if show_unseen_users
            else [user.id for user in self.unseen_users]
        }

    @staticmethod
    def generate_log(alert: str, description: str, unseen_users: list["UserModel"], user: "UserModel" = None) -> "LogEntryModel":
        return LogEntryModel(
            alert=alert,
            time=datetime.now(),
            description=description,
            user=user,
            unseen_users=unseen_users
        )

    def seen_by_user(self, user : "UserModel"):
        """Remove a user from unseen users"""
        self.unseen_users.remove(user)