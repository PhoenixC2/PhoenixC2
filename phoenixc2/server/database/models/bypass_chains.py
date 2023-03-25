"""The Credentials Model"""

from typing import List, Tuple, Dict, Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime


from phoenixc2.server.database.base import Base

from phoenixc2.server.bypasses import get_bypass, BaseBypass
from .users import UserModel

if TYPE_CHECKING:
    from phoenixc2.server.kits.base_payload import FinalPayload


class BypassChainModel(Base):
    """The Bypass Chain Model"""

    __tablename__ = "BypassChains"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(20))
    description: Mapped[Optional[str]] = mapped_column(String(100))
    # format: [(bypass_category, bypass_name, bypass_options)]
    bypasses: Mapped[Optional[List[Tuple[str, str, Dict[str, any]]]]] = mapped_column(
        MutableList.as_mutable(JSON), default=[]
    )
    creator_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("Users.id"),
        default=lambda: UserModel.get_current_user().id
        if UserModel.get_current_user()
        else None,
    )
    creator: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="created_bypass_chains",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    def to_dict(self) -> dict:
        """Returns the model as a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "bypasses": [bypass.to_dict() for bypass in self.get_bypasses()],
        }

    def get_bypasses(self) -> List[BaseBypass]:
        """Returns the bypasses for the chain."""
        return [get_bypass(category, name) for category, name, _ in self.bypasses]

    def create(self, data: dict) -> None:
        """Creates a bypass chain."""
        self.name = data["name"]
        self.description = data["description"]
        self.creator = UserModel.get_current_user()

    def add_bypass(self, category: str, bypass: str, options: dict = None) -> None:
        """Adds a bypass to the chain."""

        if self.bypasses:
            last_bypass = self.bypasses[-1]
            if get_bypass(last_bypass[0], last_bypass[1]).final:
                raise ValueError("Cannot add a bypass to a final bypass.")
        self.bypasses.append((category, bypass, options or {}))

    def remove_bypass(self, index: int) -> None:
        """Removes a bypass from the chain."""
        if index >= len(self.bypasses):
            raise IndexError("Index out of range.")
        self.bypasses.pop(index)

    def move_bypass(self, index: int, new_index: int) -> None:
        """Moves a bypass in the chain."""
        if index >= len(self.bypasses) or new_index >= len(self.bypasses):
            raise IndexError("Index out of range.")
        self.bypasses.insert(new_index, self.bypasses.pop(index))

    def update_bypass(self, index: int, options: dict) -> None:
        """Updates the options for a bypass."""
        if index >= len(self.bypasses):
            raise IndexError("Index out of range.")
        self.bypasses[index][2] = options

    def execute(self, final_payload: "FinalPayload") -> "FinalPayload":
        """Generate the bypassed payload using a generated payload"""

        for category, name, args in self.bypasses:
            get_bypass(category, name).execute(final_payload, args)

        return final_payload

    def __repr__(self) -> str:
        return (
            f"<BypassChainModel(id={self.id}, name={self.name},"
            f" bypasses={len(self.bypasses)})>"
        )
