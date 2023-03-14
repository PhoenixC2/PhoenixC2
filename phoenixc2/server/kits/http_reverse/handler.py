from phoenixc2.server.database import DeviceModel, ListenerModel

from ..base_handler import BaseHandler


class Handler(BaseHandler):
    """The Reverse Http(s) Handler Class to interact with the Device"""

    def __init__(self, db_entry: DeviceModel, listener: ListenerModel):
        super().__init__(db_entry, listener)

    def alive(self) -> bool:
        return self.db_entry.connected if self.db_entry is not None else False
