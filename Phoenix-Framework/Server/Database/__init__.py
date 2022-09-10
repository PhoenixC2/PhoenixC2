from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .devices import DeviceModel
from .listeners import ListenerModel
from .stagers import StagerModel
from .users import UserModel
from .logentry import LogEntryModel
from .credentials import CredentialModel

engine = create_engine("sqlite:///Data/db.sqlite3", connect_args={'check_same_thread': False})
db_session = sessionmaker(bind=engine)()

