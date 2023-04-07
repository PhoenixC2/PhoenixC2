"""The Log Entries Model"""
import ipaddress
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional

from flask import request
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.datastructures import FileStorage

from phoenixc2.server.database.base import Base
from phoenixc2.server.database.engine import Session
from phoenixc2.server.utils.resources import PICTURES, get_resource
from phoenixc2.server.utils.web import generate_html_from_markdown

from .association import user_operation_assignment_table
from .users import UserModel

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander

    from .credentials import CredentialModel
    from .listeners import ListenerModel
    from .logs import LogEntryModel


class OperationModel(Base):
    """The Operation Model"""

    __tablename__ = "Operations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    expiry: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.today() + timedelta(days=30)
    )
    picture: Mapped[Optional[bool]] = mapped_column(Boolean)
    subnets: Mapped[List[str]] = mapped_column(MutableList.as_mutable(JSON), default=[])
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    owner_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("Users.id"),
        default=lambda: UserModel.get_current_user().id
        if UserModel.get_current_user()
        else None,
    )
    owner: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="owned_operations",
    )
    assigned_users: Mapped[List["UserModel"]] = relationship(
        "UserModel",
        back_populates="assigned_operations",
        secondary=user_operation_assignment_table,
    )
    listeners: Mapped[List["ListenerModel"]] = relationship(
        "ListenerModel",
        back_populates="operation",
    )
    credentials: Mapped[List["CredentialModel"]] = relationship(
        "CredentialModel",
        back_populates="operation",
    )
    logs: Mapped[List["LogEntryModel"]] = relationship(
        "LogEntryModel",
        back_populates="operation",
    )

    def to_dict(
        self,
        show_owner: bool = False,
        show_assigned_users: bool = False,
        show_listeners: bool = False,
        show_credentials: bool = False,
        show_logs: bool = False,
    ) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "expiry": self.expiry,
            "picture": self.picture,
            "subnets": self.subnets,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "owner": self.owner.to_dict() if show_owner else self.owner.id,
            "users": [user.to_dict() for user in self.assigned_users]
            if show_assigned_users
            else [user.id for user in self.assigned_users],
            "listeners": [listener.to_dict() for listener in self.listeners]
            if show_listeners
            else [listener.id for listener in self.listeners],
            "credentials": [credential.to_dict() for credential in self.credentials]
            if show_credentials
            else [credential.id for credential in self.credentials],
            "logs": [log.to_dict() for log in self.logs]
            if show_logs
            else [log.id for log in self.logs],
        }

    def delete(
        self,
        commander: "Commander",
        delete_elements: bool = False,
    ) -> None:
        """Delete the operation from the database."""
        self.delete_picture()
        if delete_elements:
            for device in self.devices:
                device.delete()
            for listener in self.listeners:
                listener.delete(True, commander)
            for log in self.logs:
                Session.delete(log)
            for credential in self.credentials:
                Session.delete(credential)
        Session.delete(self)

    def get_picture(self) -> str:
        """Get the picture"""
        return (
            str(get_resource(PICTURES, f"{self.id}-operation"))
            if self.picture
            else get_resource("web/static/images", "icon.png")
        )

    def set_picture(self, file: FileStorage) -> None:
        """Set the picture and save it"""

        if self.picture:
            get_resource(PICTURES, f"{self.id}-operation").unlink()
 
        self.picture = True
        file.save(
            get_resource(PICTURES, f"{self.id}-operation", skip_file_check=True)
        )

    def delete_picture(self) -> None:
        """Delete the profile picture"""
        if self.picture:
            get_resource(PICTURES, f"{self.id}-operation").unlink()
            self.picture = False

    def assign_user(self, user: "UserModel") -> None:
        """Assign a user to the operation."""
        if user == self.owner:
            raise ValueError("Owner cannot be assigned to his own operation.")
        if user not in self.assigned_users:
            self.assigned_users.append(user)

    def unassign_user(self, user: "UserModel") -> None:
        """Unassign a user from the operation."""
        if user in self.assigned_users:
            self.assigned_users.remove(user)
        else:
            raise ValueError(f"User {user.username} is not assigned to this operation.")

    def add_subnet(self, subnet: str) -> None:
        """Add a subnet to the operation."""
        try:
            ipaddress.ip_network(subnet)
        except ValueError:
            raise ValueError("Invalid subnet")
        else:
            self.subnets.append(subnet)

    def remove_subnet(self, subnet: str) -> None:
        """Remove a subnet from the operation."""
        if subnet not in self.subnets:
            self.subnets.remove(subnet)
        else:
            raise ValueError(f"Subnet {subnet} is not assigned to this operation.")

    def edit(self, data: dict) -> None:
        """Edit the operation."""
        for key, value in data.items():
            if key == "name":
                self.name = value
            elif key == "description":
                try:
                    generate_html_from_markdown(value)
                except SyntaxError:
                    raise ValueError("Invalid markdown")
                else:
                    self.description = value
            elif key == "expiry":
                try:
                    self.expiry = datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Invalid expiry date")
            else:
                raise ValueError(f"Invalid Change: {key}")

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        expiry: datetime = None,
    ) -> "OperationModel":
        """Add a new operation to the database."""
        operation = cls(
            name=name,
            description=description,
        )
        if expiry is not None:
            try:
                operation.expiry = datetime.strptime(expiry, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid expiry date: Format must be YYYY-MM-DD")
        return operation

    @staticmethod
    def get_current_operation() -> "OperationModel":
        """Get the current operation and check if the user is assigned to it."""
        try:
            operation = (
                Session.query(OperationModel)
                .filter_by(id=request.cookies.get("operation"))
                .first()
            )
        except Exception:
            return None
        if (
            operation is not None
            and UserModel.get_current_user()
            in operation.assigned_users + [operation.owner]
        ):
            return operation
        else:
            return None

    def __repr__(self) -> str:
        return f"<OperationModel(id={self.id}, name={self.name})>"
