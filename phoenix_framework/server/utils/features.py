from dataclasses import dataclass


@dataclass
class Feature:
    """Feature class which is used to show features of listeners & payloads"""

    name: str
    description: str
    pro: bool = True

    def to_dict(self):
        return {"name": self.name, "description": self.description, "pro": self.pro}
