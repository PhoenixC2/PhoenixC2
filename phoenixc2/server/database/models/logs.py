"""The Log Entries Model"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped
from phoenixc2.server.utils.dates import (
    convert_to_unix_timestamp,
)
from phoenixc2.server.database.base import Base
from phoenixc2.server.database.engine import Session
from phoenixc2.server.utils.ui import log as cli_log

from .association import user_logentry_association_table
from .operations import OperationModel
from .users import UserModel


class LogEntryModel(Base):
    """The Log Entries Model"""

    __tablename__ = "Logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # info|alert|error|critical|success
    status: Mapped[str] = mapped_column(String(10))
    endpoint: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text(100))
    time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    operation_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("Operations.id")
    )
    operation: Mapped["OperationModel"] = relationship(
        "OperationModel", back_populates="logs"
    )
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("Users.id"))
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="logs"
    )  # user who triggered the log creation
    unseen_users: Mapped[List["UserModel"]] = relationship(
        "UserModel",
        secondary=user_logentry_association_table,
        back_populates="unseen_logs",
    )  # users who haven't seen this message

    def to_dict(
        self,
        show_user: bool = False,
        show_unseen_users: bool = False,
        show_operation: bool = False,
    ) -> dict:
        data = {
            "id": self.id,
            "status": self.status,
            "endpoint": self.endpoint,
            "description": self.description,
            "time": convert_to_unix_timestamp(self.time),
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

    @classmethod
    def create(
        cls,
        status: str,
        endpoint: str,
        description: str,
        unseen_users: list["UserModel"],
        user: "UserModel" = None,
    ) -> "LogEntryModel":
        return cls(
            status=status,
            endpoint=endpoint,
            description=description,
            user=user,
            unseen_users=unseen_users,
        )

    @classmethod
    def log(
        cls,
        status: str,
        endpoint: str,
        description: str,
        user: "UserModel" = None,
        log_to_cli: bool = True,
    ) -> "LogEntryModel":
        """Log an entry to the database and CLI"""
        if log_to_cli:
            cli_log(f"({user if user is not None else 'System'}) {description}", status)
        log = cls.create(
            status, endpoint, description, Session.query(UserModel).all(), user
        )
        Session.add(log)
        Session.commit()
        return log

    def __repr__(self) -> str:
        return (
            f"<LogEntry(id={self.id}, status={self.status}, "
            f"description={self.description})>"
        )
