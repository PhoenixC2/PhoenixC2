"""The association table between different models."""
from sqlalchemy import Column, ForeignKey, String, Table

from phoenixc2.server.database.base import Base

user_logentry_association_table = Table(
    "user_logentry_association",
    Base.metadata,
    Column("user_id", ForeignKey("Users.id"), primary_key=True),
    Column("logentry_id", ForeignKey("Logs.id"), primary_key=True),
)

user_operation_assignment_table = Table(
    "operation_user_assignment",
    Base.metadata,
    Column("operation_id", ForeignKey("Operations.id"), primary_key=True),
    Column("user_id", ForeignKey("Users.id"), primary_key=True),
)
