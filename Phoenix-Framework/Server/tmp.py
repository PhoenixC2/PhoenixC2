import os

os.environ["PHOENIX_CONFIG_PATH"] = "/home/screamz/Code/Phoenix-Framework/Phoenix-Framework/Server/Data/config.toml"
from datetime import datetime
from uuid import uuid1

from Database import *

task = TaskModel(
    name=str(uuid1()),
    device=Session.query(DeviceModel).first(),
    type="rce",
    args=["whoami"],
    created_at=datetime.now()
)
Session.add(task)
Session.commit()