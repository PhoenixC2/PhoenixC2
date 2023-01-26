"""The Log Entries Model"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from phoenixc2.server.database.base import Base
from phoenixc2.server.database.engine import Session
from phoenixc2.server.utils.ui import log as cli_log

from .association import user_logentry_association_table
from .operations import OperationModel
from .users import UserModel


class LogEntryModel(Base):
    """The Log Entries Model"""

    __tablename__ = "Logs"
    id: int = Column(Integer, primary_key=True, nullable=False)
    # info|alert|error|critical|success
    alert: str = Column(String(10), name="type")
    endpoint = Column(String(50))
    description: str = Column(Text(100))
    time: datetime = Column(DateTime, default=datetime.now)
    operation_id: int = Column(Integer, ForeignKey("Operations.id"))
    operation: "OperationModel" = relationship("OperationModel", back_populates="logs")
    user_id: int = Column(Integer, ForeignKey("Users.id"))
    user: "UserModel" = relationship(
        "UserModel", back_populates="logs"
    )  # user who triggered the log creation
    unseen_users: list["UserModel"] = relationship(
        "UserModel",
        secondary=user_logentry_association_table,
        back_populates="unseen_logs",
    )  # users who haven't seen this message
    operation_id = Column(
        Integer,
        ForeignKey("Operations.id"),
        default=lambda: OperationModel.get_current_operation().id
        if OperationModel.get_current_operation() is not None
        else None,
    )
    operation = relationship("OperationModel", back_populates="logs")

    def to_dict(
        self,
        show_user: bool = False,
        show_unseen_users: bool = False,
        show_operation: bool = False,
    ) -> dict:
        data = {
            "id": self.id,
            "alert": self.alert,
            "endpoint": self.endpoint,
            "description": self.description,
            "time": self.time,
            "unseen_users": [user.to_dict() for user in self.unseen_users]
            if show_unseen_users
            else [user.id for user in self.unseen_users],
        }
        if self.user is not None and show_user:
            data["user"] = self.user.to_dict()
        else:
            data["user"] = self.user.id if self.user is not None else "System"
        if self.operation is not None and show_operation:
            data["operation"] = self.operation.to_dict()
        else:
            data["operation"] = (
                self.operation.id if self.operation is not None else None
            )
        return data

    def seen_by_user(self, user: "UserModel"):
        """Remove a user from unseen users"""
        if user in self.unseen_users:
            self.unseen_users.remove(user)

    @classmethod
    def create(
        cls,
        alert: str,
        endpoint: str,
        description: str,
        unseen_users: list["UserModel"],
        user: "UserModel" = None,
    ) -> "LogEntryModel":
        return cls(
            alert=alert,
            endpoint=endpoint,
            description=description,
            user=user,
            unseen_users=unseen_users,
        )

    @classmethod
    def log(
        cls,
        alert: str,
        endpoint: str,
        description: str,
        user: "UserModel" = None,
        log_to_cli: bool = True,
    ) -> "LogEntryModel":
        """Log an entry to the database"""
        if log_to_cli:
            cli_log(f"({user if user is not None else 'System'}) {description}", alert)
        log = cls.create(
            alert, endpoint, description, Session.query(UserModel).all(), user
        )
        Session.add(log)
        Session.commit()
        return log
