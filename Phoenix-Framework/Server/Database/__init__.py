from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Utils.config import load_config
from Utils.ui import log

from .credentials import CredentialModel
from .devices import DeviceModel
from .listeners import ListenerModel
from .logentry import LogEntryModel
from .operations import OperationModel
from .stagers import StagerModel
from .tasks import TasksModel
from .users import UserModel

c = load_config()["database"]
if c["type"] == "sqlite":
    engine = create_engine(f"sqlite:///{c['sqlite_location']}", connect_args={'check_same_thread': False})
else:
    conn_string = f"{c['type']}://{c['user']}:{c['pass']}@{c['host']}:{c['port']}/{c['database']}"
    engine = create_engine(conn_string)

    
db_session = sessionmaker(bind=engine)()

