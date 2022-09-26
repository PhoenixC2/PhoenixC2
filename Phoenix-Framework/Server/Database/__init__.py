from sqlalchemy import create_engine
from sqlalchemy.orm import Session as Session_Type
from sqlalchemy.orm import scoped_session, sessionmaker
from Utils.config import load_config

from .credentials import CredentialModel
from .devices import DeviceModel
from .listeners import ListenerModel
from .logentries import LogEntryModel
from .operations import OperationModel
from .stagers import StagerModel
from .tasks import TaskModel
from .users import UserModel

c = load_config()["database"]
if c["type"] == "sqlite":
    engine = create_engine(f"sqlite:///{c['sqlite_location']}")
else:
    conn_string = f"{c['type']}://{c['user']}:{c['pass']}@{c['host']}:{c['port']}/{c['database']}"
    engine = create_engine(conn_string)

Session : Session_Type  = scoped_session(sessionmaker(bind=engine))