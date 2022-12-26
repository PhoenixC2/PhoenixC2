import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session as Session_Type
from sqlalchemy.orm import scoped_session, sessionmaker

from phoenix.server.utils.config import load_config
from phoenix.server.utils.resources import get_resource

from .association import (user_logentry_association_table,
                          user_operation_assignment_table)
from .credentials import CredentialModel
from .devices import DeviceModel
from .listeners import ListenerModel
from .logs import LogEntryModel
from .operations import OperationModel
from .stagers import StagerModel
from .tasks import TaskModel
from .users import UserModel

c = load_config()["database"]

if c["type"] == "sqlite":
    conn_string = (
        "sqlite:///"
        + str(get_resource("data", c["sqlite_name"], skip_file_check=True))
        + ".sqlite3"
    )

else:
    conn_string = (
        f"{c['type']}://{c['user']}:{c['pass']}@{c['host']}:{c['port']}/{c['database']}"
    )

# check if database verbose is enabled
if "3" in os.getenv("PHOENIX_DEBUG", "") or "4" in os.getenv("PHOENIX_DEBUG", ""):
    engine = create_engine(conn_string, echo=True)
else:
    engine = create_engine(conn_string)

Session: Session_Type = scoped_session(sessionmaker(bind=engine))
