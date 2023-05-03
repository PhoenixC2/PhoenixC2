from abc import abstractmethod, ABC

from phoenixc2.server.database import DeviceModel, ListenerModel, Session, TaskModel
from phoenixc2.server.modules.base import BaseModule


class BaseHandler(ABC):
    """The Base Handler Class for all Devices"""

    def __repr__(self) -> TaskModel:
        return str(self.addr)

    def __init__(self, db_entry: DeviceModel, listener: ListenerModel):
        self.addr = db_entry.address
        self.id = db_entry.id
        self.name = db_entry.name
        self.modules: list[BaseModule] = []
        self.listener = listener

    @property
    def db_entry(self) -> DeviceModel:
        return Session().query(DeviceModel).filter_by(id=self.id).first()

    def add_task(self, task: TaskModel):
        self.tasks.append(task)

    def get_task(self, id_or_name: int | str) -> TaskModel:
        """Return a task based on its id or name."""
        if type(id_or_name) == int:
            for task in self.db_entry.tasks:
                if task.id == id_or_name:
                    return task
        else:
            for task in self.db_entry.tasks:
                if task.name == id_or_name:
                    return task

    @abstractmethod
    def alive(self) -> bool:
        """Checks if device is alive

        Returns:
            bool: True if yes, False if not
        """
