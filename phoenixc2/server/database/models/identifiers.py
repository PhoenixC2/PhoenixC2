"""The Device Identifier Model"""
from datetime import datetime
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from phoenixc2.server.utils.dates import (
    convert_to_unix_timestamp,
)
from phoenixc2.server.database.base import Base
from phoenixc2.server.database.engine import Session

if TYPE_CHECKING:
    from phoenixc2.server.database import DeviceModel
    from phoenixc2.server.commander.commander import Commander


class DeviceIdentifierModel(Base):
    """The Device Identifier Model
    This model is used to reidentify a device.
    """

    __mapper_args__ = {
        "confirm_deleted_rows": False
    }  # required to avoid error bc of cascade delete
    __tablename__ = "Identifiers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uid: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    device_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("Devices.id"))
    device: Mapped["DeviceModel"] = relationship(
        "DeviceModel", back_populates="identifier"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    @classmethod
    def generate(cls, uid: str) -> "DeviceIdentifierModel":
        """Generate a new device identifier"""
        if not uid:
            uid = uuid.uuid4().hex
        return cls(uid=uid)

    @classmethod
    def get_or_create(cls, uid: str) -> Optional["DeviceIdentifierModel"]:
        """Returns an existing device identifier or generates a new one"""
        identifier = Session.query(cls).filter_by(uid=uid).first()

        if identifier is None:
            identifier = cls.generate(uid)
            Session.add(identifier)
            Session.commit()

        return identifier

    def __repr__(self) -> str:
        return f"<DeviceIdentifier(uid={self.uid}, device={self.device.id})>"

    def to_dict(self, commander: "Commander", show_device: bool = False) -> dict:
        """Convert the model to a dictionary"""
        return {
            "id": self.id,
            "uid": self.uid,
            "device": self.device.to_dict(commander)
            if show_device
            else self.device.id
            if self.device
            else None,
            "created_at": convert_to_unix_timestamp(self.created_at),
            "updated_at": convert_to_unix_timestamp(self.updated_at),
        }
