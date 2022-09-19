from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .credentials import CredentialModel
from .devices import DeviceModel
from .listeners import ListenerModel
from .logentry import LogEntryModel
from .operations import OperationModel
from .stagers import StagerModel
from .users import UserModel
from .tasks import TasksModel
engine = create_engine("sqlite:///Data/db.sqlite3", connect_args={'check_same_thread': False})
db_session = sessionmaker(bind=engine)()

