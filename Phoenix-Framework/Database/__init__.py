from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .devices import DeviceModel
from .listeners import ListenerModel
from .stagers import StagerModel
from .users import UserModel
from .logentry import LogEntryModel

engine = create_engine("sqlite:///Data/db.sqlite3")
db_session = sessionmaker(bind=engine)()

