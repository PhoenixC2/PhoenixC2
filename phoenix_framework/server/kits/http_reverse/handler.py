from datetime import datetime

from phoenix_framework.server.database import DeviceModel, Session, TaskModel

from ..base_handler import BaseHandler


class Handler(BaseHandler):
    """The Reverse Http(s) Handler Class to interact with the Device"""

    def __init__(self, db_entry: DeviceModel):
        super().__init__(db_entry)

    def alive(self) -> bool:
        return self.db_entry.connected