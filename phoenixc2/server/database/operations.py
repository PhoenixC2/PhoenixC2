"""The Log Entries Model"""
import ipaddress
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from flask import request
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship

from phoenixc2.server.utils.web import generate_html_from_markdown

from .association import user_operation_assignment_table
from .base import Base
from .users import UserModel
from .engine import Session

if TYPE_CHECKING:
    from phoenixc2.server.commander import Commander
    from sqlalchemy.orm import Session as SessionType
    from .credentials import CredentialModel
    from .devices import DeviceModel
    from .listeners import ListenerModel
    from .logs import LogEntryModel


class OperationModel(Base):
    """The Operation Model"""

    __tablename__ = "Operations"
    id: int = Column(Integer, primary_key=True, nullable=False)
    name: str = Column(String(100), nullable=False)
    description: str = Column(Text, default="")
    expiry: datetime = Column(
        DateTime, default=lambda: datetime.today() + timedelta(days=30)
    )
    subnets: list[str] = Column(MutableList.as_mutable(JSON), default=[])
    created_at: datetime = Column(DateTime, default=datetime.now)
    updated_at: datetime = Column(DateTime, onupdate=datetime.now)
    owner_id: int = Column(Integer, ForeignKey("Users.id"), nullable=False)
    owner: "UserModel" = relationship(
        "UserModel",
        back_populates="owned_operations",
    )
    assigned_users: list["UserModel"] = relationship(
        "UserModel",
        back_populates="assigned_operations",
        secondary=user_operation_assignment_table,
    )
    devices: list["DeviceModel"] = relationship(
        "DeviceModel", back_populates="operation"
    )
    listeners: list["ListenerModel"] = relationship(
        "ListenerModel",
        back_populates="operation",
    )
    credentials: list["CredentialModel"] = relationship(
        "CredentialModel",
        back_populates="operation",
    )
    logs: list["LogEntryModel"] = relationship(
        "LogEntryModel",
        back_populates="operation",
    )

    def to_dict(
        self,
        show_owner: bool = False,
        show_assigned_users: bool = False,
        show_devices: bool = False,
        show_listeners: bool = False,
        show_credentials: bool = False,
        show_logs: bool = False,
    ) -> dict:
        return {
            "id": self.log_id,
            "type": self.log_type,
            "expiry": self.expiry,
            "description": self.description,
            "subnets": self.subnets,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "owner": self.owner.to_dict() if show_owner else self.owner.id,
            "users": [user.to_dict() for user in self.assigned_users]
            if show_assigned_users
            else [user.id for user in self.assigned_users],
            "devices": [device.to_dict() for device in self.assigned_devices]
            if show_devices
            else [device.id for device in self.assigned_devices],
            "listeners": [listener.to_dict() for listener in self.assigned_listeners]
            if show_listeners
            else [listener.id for listener in self.assigned_listeners],
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

    def assign_user(self, user: "UserModel") -> None:
        """Assign a user to the operation."""
        if user not in self.assigned_users:
            self.assigned_users.append(user)

    def unassign_user(self, user: "UserModel") -> None:
        """Unassign a user from the operation."""
        if user in self.assigned_users:
            self.assigned_users.remove(user)

    def add_subnet(self, subnet: str) -> None:
        """Add a subnet to the operation."""
        try:
            ipaddress.ip_network(subnet)
        except ValueError:
            raise ValueError("Invalid Subnet")
        else:
            self.subnets.append(subnet)

    def remove_subnet(self, subnet: str) -> None:
        """Remove a subnet from the operation."""
        self.subnets.remove(subnet)
    def edit(self, data: dict) -> None:
        """Edit the operation."""
        for key, value in data.items():
            if key == "name":
                self.name = value
            elif key == "description":
                try:
                    generate_html_from_markdown(value)
                except SyntaxError:
                    raise ValueError("Invalid Markdown")
                else:
                    self.description = value
            elif key == "expiry":
                self.expiry = value
            elif key == "subnets":
                self.subnets = value
            else:
                raise ValueError(f"Invalid Change: {key}")

    @classmethod
    def add(
        cls,
        name: str,
        description: str,
        expiry: datetime,
        subnets: list[str],
        owner: "UserModel",
    ) -> "OperationModel":
        """Add a new operation to the database."""
        operation = cls(
            name=name,
            description=description,
            expiry=expiry,
            subnets=subnets,
            owner=owner,
        )
        return operation

    @staticmethod
    def get_current_operation() -> "OperationModel":
        """Get the current operation and check if the user is assigned to it."""
        operation = (
            Session.query(OperationModel)
            .filter_by(id=request.cookies.get("operation"))
            .first()
        )

        if (
            operation is not None
            and UserModel.get_current_user() in operation.assigned_users
        ):
            return operation
        else:
            return None

    @staticmethod
    def change_current_operation(operation_id: int) -> "OperationModel":
        """Change the current operation."""
        operation = Session.query(OperationModel).filter_by(id=operation_id).first()

        if operation is not None:
            raise ValueError("Operation does not exist")

        if UserModel.get_current_user() not in operation.assigned_users:
            raise ValueError("User not assigned to operation")
        
        request.cookies.add("operation", operation_id)
        return operation
