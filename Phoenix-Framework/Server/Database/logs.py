"""The Log Entries Model"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Session, relationship
from Utils.ui import log as cli_log
from .base import Base
from .users import user_logentry_association_table, UserModel


class LogEntryModel(Base):
    """The Log Entries Model"""
    __tablename__ = "Logs"
    id: int = Column(Integer, primary_key=True,
                     nullable=False)
    # info|alert|error|critical|success
    alert: str = Column(String(10), name="type")
    endpoint = Column(String(50))
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

    def to_dict(self, show_user: bool = True, show_unseen_users: bool = True) -> dict:
        data = {
            "id": self.id,
            "alert": self.alert,
            "endpoint": self.endpoint,
            "time": self.time,
            "description": self.description,
            "unseen_users": [user.to_dict(show_logs=False, show_unseen_logs=False) for user in self.unseen_users] if show_unseen_users
            else [user.id for user in self.unseen_users]
        }
        if self.user is not None and show_user:
            data["user"] = self.user.to_dict(
                show_logs=False, show_unseen_logs=False)
        else:
            data["user"] = self.user.id if self.user is not None else "System"
        return data

    def seen_by_user(self, user: "UserModel"):
        """Remove a user from unseen users"""
        if user in self.unseen_users:
            self.unseen_users.remove(user)

    @classmethod
    def generate_log(cls, alert: str, endpoint: str, description: str, unseen_users: list["UserModel"], user: "UserModel" = None) -> "LogEntryModel":
        return cls(
            alert=alert,
            time=datetime.now(),
            description=description,
            user=user,
            unseen_users=unseen_users
        )

    @classmethod
    def log(cls, alert: str, endpoint: str, description: str, session: Session, user: "UserModel" = None, log_to_cli: bool = True) -> "LogEntryModel":
        """Log an entry to the database"""
        if log_to_cli:
            cli_log(f"({user if user is not None else 'System'}) {description}", alert)
        log = cls.generate_log(
            alert, endpoint, description, session.query(UserModel).all(), user)
        session.add(log)
        session.commit()
        return log
