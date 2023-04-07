from ..handler_base import BaseHandler


class Handler(BaseHandler):
    """The Reverse Http(s) Handler Class to interact with the Device"""

    def alive(self) -> bool:
        return self.db_entry.connected if self.db_entry is not None else False
