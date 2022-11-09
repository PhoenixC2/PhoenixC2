from database import DeviceModel

from ..base_handler import BaseHandler


class Handler(BaseHandler):
    """The example handler"""

    def __init__(self, db_entry: DeviceModel):
        super().__init__(db_entry)

    def alive(self) -> bool:
        return self.db_entry.connected
