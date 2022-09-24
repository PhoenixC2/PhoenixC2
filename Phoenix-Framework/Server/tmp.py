import os
os.environ["PHOENIX_CONFIG_PATH"] = "/home/screamz/Code/Phoenix-Framework/Phoenix-Framework/Server/Data/config.toml"
from Database import *
from datetime import datetime
from uuid import uuid1


task = TasksModel(
    name=str(uuid1()),
    device=db_session.query(DeviceModel).first(),
    type="rce",
    args=["whoami"],
    created_at=datetime.now()
)
db_session.add(task)
db_session.commit()