"""The Credentials Model"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped

from .operations import OperationModel

from phoenixc2.server.database.base import Base


class CredentialModel(Base):
    """The Credentials Model"""

    __tablename__ = "Credentials"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(String(100))
    hash: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text(500))
    user: Mapped[str] = mapped_column(String(100))
    admin: Mapped[bool] = mapped_column(Boolean, default=False)
    found_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
    operation_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("Operations.id"),
        default=lambda: OperationModel.get_current_operation().id
        if OperationModel.get_current_operation() is not None
        else None,
    )
    operation: Mapped["OperationModel"] = relationship(
        "OperationModel", back_populates="credentials"
    )

    def to_dict(self, show_operation: bool = False) -> dict:
        return {
            "id": self.id,
            "value": self.value,
            "hash": self.hash,
            "notes": self.notes,
            "user": self.user,
            "admin": self.admin,
            "found_at": self.found_at,
            "updated_at": self.updated_at,
            "operation": self.operation.to_dict()
            if show_operation and self.operation is not None
            else self.operation_id,
        }

    @classmethod
    def create(
        cls,
        value: str,
        hash: bool,
        user: str,
        admin: bool,
        notes: str = None,
    ) -> "CredentialModel":
        return cls(
            value=value,
            hash=hash,
            user=user,
            admin=admin,
            notes=notes,
            operation=OperationModel.get_current_operation(),
        )
