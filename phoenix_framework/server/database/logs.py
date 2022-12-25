"""The Log Entries Model"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Session, relationship

from phoenix_framework.server.utils.ui import log as cli_log

from .association import user_logentry_association_table
from .base import Base
from .users import UserModel
if TYPE_CHECKING:
    from .operations import OperationModel



class LogEntryModel(Base):
    """The Log Entries Model"""

    __tablename__ = "Logs"
    id: int = Column(Integer, primary_key=True, nullable=False)
    # info|alert|error|critical|success
    alert: str = Column(String(10), name="type")
    endpoint = Column(String(50))
    description: str = Column(Text(100))
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
    time: datetime = Column(DateTime, default=datetime.now)

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
            "unseen_users": [user.to_dict() for user in self.unseen_users]
            if show_unseen_users
            else [user.id for user in self.unseen_users],
            "time": self.time,
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
    def generate_log(
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
        session: Session,
        user: "UserModel" = None,
        log_to_cli: bool = True,
    ) -> "LogEntryModel":
        """Log an entry to the database"""
        if log_to_cli:
            cli_log(f"({user if user is not None else 'System'}) {description}", alert)
        log = cls.generate_log(
            alert, endpoint, description, session.query(UserModel).all(), user
        )
        session.add(log)
        session.commit()
        return log
