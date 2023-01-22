"""The Credentials Model"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from .operations import OperationModel

from phoenixc2.server.database.base import Base


class CredentialModel(Base):
    """The Credentials Model"""

    __tablename__ = "Credentials"
    id: int = Column(Integer, primary_key=True, nullable=False)
    credential: str = Column(String(100))
    hash: bool = Column(Boolean, default=False)
    notes: str = Column(Text(500))
    user: str = Column(String(100))
    admin: bool = Column(Boolean, default=False)
    found_at: datetime = Column(DateTime, default=datetime.now)
    updated_at: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    operation_id: int = Column(
        Integer,
        ForeignKey("Operations.id"),
        default=lambda: OperationModel.get_current_operation().id
        if OperationModel.get_current_operation() is not None
        else None,
    )
    operation: "OperationModel" = relationship(
        "OperationModel", back_populates="credentials"
    )

    def to_dict(self, show_operation: bool = False) -> dict:
        return {
            "id": self.id,
            "credential": self.credential,
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
        admin: bool,
        credential: str,
        hash: bool,
        user: str,
        notes: str = None,
    ) -> "CredentialModel":
        credential = cls(
            user=user,
            admin=admin,
            credential=credential,
            hash=hash,
            notes=notes,
        )
        return credential
