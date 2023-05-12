"""The Users Model"""
import json
import os
from datetime import datetime
from functools import wraps
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid1

from flask import request, session
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped
from werkzeug.security import check_password_hash, generate_password_hash

from phoenixc2.server.database.base import Base
from phoenixc2.server.database.engine import Session
from phoenixc2.server.utils.resources import get_resource, PICTURES
from phoenixc2.server.utils.misc import Status

from .association import (
    user_logentry_association_table,
    user_operation_assignment_table,
)


if TYPE_CHECKING:
    from .logs import LogEntryModel
    from .operations import OperationModel


class UserModel(Base):
    """The Users Model"""

    __tablename__ = "Users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text)
    _api_key: Mapped[str] = mapped_column(
        String(30),
        name="api_key",
        nullable=False,
        unique=True,
        default=lambda: str(uuid1()),
    )
    admin: Mapped[bool] = mapped_column(Boolean)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    profile_picture: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_activity: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=datetime.now
    )
    logs: Mapped[List["LogEntryModel"]] = relationship(
        "LogEntryModel", back_populates="user"
    )  # Logs triggered by user
    unseen_logs: Mapped[List["LogEntryModel"]] = relationship(
        "LogEntryModel",
        secondary=user_logentry_association_table,
        back_populates="unseen_users",
    )  # Logs not seen by user yet
    assigned_operations: Mapped[List["OperationModel"]] = relationship(
        "OperationModel",
        secondary=user_operation_assignment_table,
        back_populates="assigned_users",
    )
    owned_operations: Mapped[List["OperationModel"]] = relationship(
        "OperationModel", back_populates="owner"
    )

    @property
    def api_key(self) -> str | None:
        """Get the API key for the user if the user requesting it is authorized"""
        try:
            curr_user = self.get_current_user()
            if (curr_user.admin and self.id != 0) or curr_user.id == self.id:
                return self._api_key
        except AttributeError:
            return self._api_key
        return None

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

    def to_dict(
        self,
        show_logs: bool = False,
        show_unseen_logs: bool = False,
        show_assigned_operations: bool = False,
        show_owned_operations: bool = False,
    ) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "api_key": self.api_key,
            "admin": self.admin,
            "disabled": self.disabled,
            "profile_picture": self.profile_picture,
            "status": self.activity_status,
            "last_login": self.last_login,
            "last_activity": self.last_activity,
            "logs": [log.to_dict() for log in self.logs]
            if show_logs
            else [log.id for log in self.logs],
            "unseen_logs": [log.to_dict() for log in self.unseen_logs]
            if show_unseen_logs
            else [log.id for log in self.unseen_logs],
            "assigned_operations": [
                operation.to_dict() for operation in self.assigned_operations
            ]
            if show_assigned_operations
            else [operation.id for operation in self.assigned_operations],
            "owned_operations": [
                operation.to_dict() for operation in self.owned_operations
            ]
            if show_owned_operations
            else [operation.id for operation in self.owned_operations],
        }

    def to_json(self, show_logs: bool = False, show_unseen_logs: bool = False) -> str:
        return json.dumps(self.to_dict(show_logs, show_unseen_logs), default=str)

    def __str__(self) -> str:
        return self.username

    def set_password(self, password: str):
        """Hash the Password and save it and generate a new API key"""
        self.password_hash = generate_password_hash(password)
        self.generate_api_key()

    def check_password(self, password: str):
        """Check if the password is right"""
        return check_password_hash(self.password_hash, password)

    def generate_api_key(self) -> None:
        """Generate a new API key"""
        self._api_key = str(uuid1())

    def edit(self, data: dict) -> None:
        """Edit the user"""
        self.username = data.get("username", self.username)

        if self.id != 1:  # don't allow editing these values for the admin user
            self.admin = data.get("admin", self.admin)
            self.disabled = data.get("disabled", self.disabled)
        else:
            raise ValueError("The user's admin and disabled status cannot be edited.")

        if data.get("password", None):
            if len(data.get("password", "")) > 50:
                raise ValueError("Password is too short")
            self.set_password(data.get("password", None))

        if len(self.username) > 50:
            raise ValueError("Username is too long")

    def delete(self) -> None:
        """Delete the user and profile picture and read all logs"""
        self.delete_profile_picture()
        Session.delete(self)

    def get_profile_picture(self) -> str:
        """Get the profile picture"""
        return (
            str(get_resource(PICTURES, f"{self.id}-user"))
            if self.profile_picture
            else None
        )

    def set_profile_picture(self, file: bytes) -> None:
        """Set the profile picture and save it"""
        if self.profile_picture:
            get_resource(PICTURES, f"{self.id}-user", skip_file_check=True).unlink()

        self.profile_picture = True
        with get_resource(PICTURES, f"{self.id}-user", skip_file_check=True).open(
            "wb"
        ) as f:
            f.write(file)

    def delete_profile_picture(self) -> None:
        """Delete the profile picture"""
        if self.profile_picture:
            get_resource(PICTURES, f"{self.id}-user", skip_file_check=True).unlink()
            self.profile_picture = False

    @classmethod
    def create(
        cls, username: str, password: str, admin: bool, disabled: bool
    ) -> "UserModel":
        """Add a new user"""
        if len(username) > 50:
            raise ValueError("Username is too long")
        if len(password) <= 8:
            raise ValueError("Password is too short")

        user = cls(
            username=username,
            admin=admin,
            disabled=disabled,
        )
        user.set_password(password)
        Session.add(user)
        return user

    @staticmethod
    def get_current_user() -> "UserModel":
        """Get the current user"""
        if request.headers.get("Api-Key") is not None:
            user = (
                Session.query(UserModel)
                .filter_by(_api_key=request.headers.get("Api-Key"))
                .first()
            )
        elif request.args.get("api_key") is not None:
            user = (
                Session.query(UserModel)
                .filter_by(_api_key=request.args.get("api_key"))
                .first()
            )
        elif session.get("api_key") is not None:
            user = (
                Session.query(UserModel)
                .filter_by(_api_key=session.get("api_key"))
                .first()
            )
        else:
            user = None
        return user if user is not None else None

    @staticmethod
    def authenticated(func):
        """Check if a user is logged in and redirect to login page if not"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            if os.getenv("PHOENIX_TEST") == "true":
                if session.get("api_key") is None:
                    session["api_key"] = Session.query(UserModel).first()._api_key
            user = UserModel.get_current_user()
            if user is None:
                return {"status": Status.Danger, "message": "You have to login."}, 401
            else:
                if user.disabled:
                    session.clear()
                    return {
                        "status": Status.Danger,
                        "message": "This account got disabled.",
                    }, 403
                user.last_activity = datetime.now()
                Session.commit()
                return func(*args, **kwargs)

        return wrapper

    @staticmethod
    def admin_required(func):
        """Check if a user is admin and redirect to login page if not"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            if os.getenv("PHOENIX_TEST") == "true":
                if session.get("api_key") is None:
                    session["api_key"] = Session.query(UserModel).first()._api_key
            user = UserModel.get_current_user()
            if user is not None:
                if user.disabled:
                    session.clear()
                    return {
                        "status": Status.Danger,
                        "message": "This account got disabled.",
                    }, 403
                if not user.admin:
                    return {
                        "status": Status.Danger,
                        "message": "You don't have the permission to do this.",
                    }, 403
                else:
                    return func(*args, **kwargs)
            else:
                return {"status": Status.Danger, "message": "You have to login."}, 401

        return wrapper
