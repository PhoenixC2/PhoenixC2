from datetime import datetime
from Handlers.base import BaseHandler
from Database import db_session, DeviceModel

class Handler(BaseHandler):
    """The Reverse Http(s) Handler Class to interact with the Device"""

    def __init__(self, addr: str, db_entry: DeviceModel):
        super().__init__(addr, db_entry)
    
    def alive(self) -> bool:
        delta = (datetime.now() - self.db_entry.last_online).seconds
        if delta < 10:
            return True
        return False 