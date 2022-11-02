import importlib
import io
from abc import abstractmethod
from datetime import datetime
from uuid import uuid1

from Database import DeviceModel, Session, TaskModel
from Modules.base import BaseModule


class BaseHandler():
    """The Base Handler Class for all Devices"""

    def __str__(self) -> TaskModel:
        return str(self.addr)

    def __init__(self, db_entry: DeviceModel):
        self.addr = db_entry.address
        self.id = db_entry.id
        self.name = db_entry.name
        self.modules: list[BaseModule] = []

    @property
    def db_entry(self) -> DeviceModel:
        return Session().query(DeviceModel).filter_by(id=self.id).first()

    def load_module(self, name: str, load_module: bool = True) -> BaseModule:
        """Load a module"""
        # Get module
        module: BaseModule = importlib.import_module(
            "Modules." + name).Module()
        if load_module:
            module.load()
        # Add to list
        self.modules.append(module)
        # Return module

        return module

    def unload_module(self, name: str):
        """Unload a module"""
        # Get module
        for module in self.modules:
            if module.name == name:
                self.modules.remove(module)
                return module
        raise FileNotFoundError("Module not found")

    def generate_task(self) -> TaskModel:
        return TaskModel(
            name=str(uuid1).split("-")[0],
            device=self.db_entry,
            created_at=datetime.now()
        )

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
