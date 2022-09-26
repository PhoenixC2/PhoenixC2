from datetime import datetime
from uuid import uuid1

from Database import DeviceModel, Session, TaskModel
from Handlers.base import BaseHandler


class Handler(BaseHandler):
    """The Reverse Http(s) Handler Class to interact with the Device"""

    def __init__(self, db_entry: DeviceModel):
        super().__init__(db_entry)
    
    def alive(self) -> bool:
        delta = (datetime.now() - self.db_entry.last_online).seconds
        if delta < 10:
            return True
        return False 
    