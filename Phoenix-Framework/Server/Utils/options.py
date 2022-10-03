"""Options for creating listeners and stagers"""
# Inspired by https://github.com/BC-SECURITY/Empire
import socket
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, MutableSequence

import requests
from Creator.available import AVAILABLE_LISTENERS, AVAILABLE_STAGERS
from Database import Session, ListenerModel
from Database.base import Base

from .misc import get_network_interfaces

if TYPE_CHECKING:
    from Commander import Commander


@dataclass
class OptionType():
    """The base option-type"""
    data_type = any = None

    @staticmethod
    def validate(name: str, data: any) -> bool:
        return data


@dataclass
class StringType(OptionType):
    """The option-type of string"""
    data_type = str

    def __str__(self) -> str:
        return "text"


@dataclass
class IntegerType(OptionType):
    """The option-type of integer"""
    data_type = int

    def __str__(self) -> str:
        return "number"


@dataclass
class BooleanType(OptionType):
    """The option-type of boolean"""
    data_type = bool

    def __str__(self) -> str:
        return "checkbox"


@dataclass
class UrlType(StringType):
    """The option-type of url"""

    @staticmethod
    def validate(name: str, url: str) -> bool:
        try:
            requests.get(url)
        except requests.ConnectionError as e:
            raise requests.ConnectionError(
                f"Couldn't connect to the url for the option '{name}'.") from e
        except requests.exceptions.MissingSchema as e:
            raise requests.exceptions.MissingSchema(
                f"The url for the option '{name}' is invalid.") from e
        except requests.exceptions.InvalidURL as e:
            raise requests.exceptions.MissingSchema(
                f"The url for the option '{name}' is invalid.") from e
        else:
            return url

    def __str__(self) -> str:
        return "url"


@dataclass
class AddressType(StringType):
    """The option-type of address"""

    @staticmethod
    def interface_to_address(interface: str) -> str:
        address = get_network_interfaces().get(interface)

        if address is None:
            raise ValueError(f"The interface '{interface}' doesn't exist.")
        return address

    @staticmethod
    def validate(name: str, address: str) -> bool:
        try:
            socket.gethostbyname(address)
        except socket.gaierror as e:
            raise socket.gaierror(
                f"{address} for the option '{name}' is invalid.") from e
        else:
            return address

    def __str__(self) -> str:
        return "address"

class PortType(IntegerType):
    """The option-type of port"""

    @staticmethod
    def validate(name: str, port: int) -> bool:
        if port < 0 or port > 65535:
            raise ValueError(f"The port '{port}' for the option '{name}' is invalid.")
        if Session.query(ListenerModel).filter_by(port=port).first():
            raise ValueError(
                f"The port '{port}' for the option '{name}' is already in use.")
        return port

    def __str__(self) -> str:
        return "port"

@dataclass
class ChoiceType(OptionType):
    choices: MutableSequence
    data_type: any

    def validate(self, name: str, choice: str) -> bool:
        if choice not in self.choices:
            raise ValueError(
                f"{choice} isn't in the available choices for '{name}'.)")
        return choice

    def __str__(self) -> str:
        return "select"


@dataclass
class TableType(OptionType):
    choices: callable 
    # allows a updated version of the choices.
    # if choices is all listeners and a new one is added it's not in the choices.
    model: any

    def validate(self, name: str, id_or_name: int | str) -> bool:
        choices = self.choices()
        if str(id_or_name).isdigit():
            object = Session.query(
                self.model).filter_by(id=id_or_name).first()
            if object not in choices:
                raise ValueError(
                    f"There's no element with the id ({id_or_name}) in the available choices for '{name}'.)")
            return object
        else:
            object = Session.query(self.model).filter_by(
                name=id_or_name).first()
            if object not in choices:
                raise ValueError(
                    f"There's no element with the name '{id_or_name}' in the available choices for '{name}'.)")
            return object

    def __str__(self) -> str:
        return "table"


@dataclass
class Option():
    """"""
    name: str
    type: OptionType
    _real_name: str = ""
    description: str = ""
    required: bool = False
    default: any = None
    editable : bool = True

    @property
    def real_name(self) -> str:
        if not self._real_name:
            return self.name.lower()
        return self._real_name

    def validate_data(self, data: any) -> OptionType.data_type:
        """Raises an exception if data isn't fitting to the requirements"""
        if not data:
            if self.required and self.default is None:
                raise ValueError(f"{self.name} is required.")
            return self.default

        if type(data) != self.type.data_type:
            try:
                data = self.type.data_type(data)
            except ValueError:
                raise TypeError(
                    f"{self.name} has to be a type of '{self.type.data_type.__name__}'.")

        data = self.type.validate(self.name, data)
        return data

    def to_json(self, commander: "Commander") -> dict:
        data = {
            "name": self.name,
            "real_name": self.real_name,
            "type": self.type.__str__(self).lower(),
            "required": self.required,
            "description": self.description,
            "default": self.default if self.default is not None else ""
        }
        if type(self.type) == ChoiceType:
            data["choices"] = self.type.choices
        elif type(self.type) == TableType:
            try:
                data["choices"] = [choice.to_json()
                                   for choice in self.type.choices()]
            except TypeError:
                data["choices"] = [choice.to_json(commander)
                                   for choice in self.type.choices()]
        return data


@dataclass
class OptionPool():
    """Contains all options"""
    options: list[Option] = field(default_factory=list)

    def register_option(self, option: Option):
        """Register a new option"""
        self.options.append(option)

    def validate_data(self, data: dict) -> dict:
        """Validate the data"""
        cleaned_data = {}
        for option in self.options:
            value = data.get(option.real_name, "")
            cleaned_data[option.real_name] = option.validate_data(value)
        return cleaned_data

    def to_json(self, commander: "Commander") -> list:
        return [option.to_json(commander) for option in self.options]
