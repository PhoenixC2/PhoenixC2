"""Options for creating listeners and stagers."""

# Inspired by https://github.com/BC-SECURITY/Empire
import socket
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, MutableSequence

import requests

from phoenixc2.server.database import ListenerModel, Session

from .misc import generate_name, get_network_interfaces

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander


@dataclass
class OptionType:
    """The base option-type"""

    data_type = None

    @staticmethod
    def validate(name: str, data: any) -> bool:
        return data

    @classmethod
    def to_dict(cls, commander: "Commander") -> dict:
        return {}


@dataclass
class StringType(OptionType):
    """The option-type of string"""

    data_type = str

    def __str__(self) -> str:
        return "string"


@dataclass
class IntegerType(OptionType):
    """The option-type of integer"""

    data_type = int

    def __str__(self) -> str:
        return "integer"


@dataclass
class BooleanType(OptionType):
    """The option-type of boolean"""

    data_type = bool

    @staticmethod
    def validate(name: str, data: any) -> bool:
        data = str(data).lower()
        if data in ("true", "on"):
            return True
        elif data in ("false", "off"):
            return False
        else:
            raise ValueError(f"'{name}' must be a boolean.")

    def __str__(self) -> str:
        return "boolean"


@dataclass
class UrlType(StringType):
    """The option-type of url"""

    @staticmethod
    def validate(name: str, url: str) -> bool:
        try:
            requests.get(url)
        except requests.ConnectionError as e:
            raise requests.ConnectionError(
                f"Couldn't connect to the url for the option '{name}'."
            ) from e
        except requests.exceptions.MissingSchema as e:
            raise requests.exceptions.MissingSchema(
                f"The url for the option '{name}' is invalid."
            ) from e
        except requests.exceptions.InvalidURL as e:
            raise requests.exceptions.MissingSchema(
                f"The url for the option '{name}' is invalid."
            ) from e
        else:
            return url

    def __str__(self) -> str:
        return "url"


@dataclass
class AddressType(StringType):
    """The option-type of address"""

    interfaces = get_network_interfaces()

    @staticmethod
    def interface_to_address(interface: str) -> str:
        address = get_network_interfaces().get(interface)

        if address is None:
            raise ValueError(f"The interface '{interface}' doesn't exist.")
        return address

    @staticmethod
    def validate(name: str, address: str) -> bool:
        if address in get_network_interfaces():
            return AddressType.interface_to_address(address)
        try:
            socket.gethostbyname(address)
        except socket.gaierror as e:
            raise socket.gaierror(
                f"{address} for the option '{name}' is invalid."
            ) from e
        else:
            return address

    def __str__(self) -> str:
        return "address"

    @classmethod
    def to_dict(cls, commander) -> dict:
        return {
            "interfaces": AddressType.interfaces,
        }


class PortType(IntegerType):
    """The option-type of port"""

    @staticmethod
    def validate(name: str, port: int) -> bool:
        if port < 0 or port > 65535:
            raise ValueError(f"The port '{port}' for the option '{name}' is invalid.")
        if Session.query(ListenerModel).filter_by(port=port).first() is not None:
            raise ValueError(
                f"The port '{port}' for the option '{name}' is already in use."
            )
        return port

    def __str__(self) -> str:
        return "port"


@dataclass
class ChoiceType(OptionType):
    choices: MutableSequence
    data_type: any

    def validate(self, name: str, choice: str) -> bool:
        if choice not in self.choices:
            raise ValueError(f"{choice} isn't in the available choices for '{name}'.)")
        return choice

    def __str__(self) -> str:
        return "choice"

    def to_dict(self, commander) -> dict:
        return {
            "choices": self.choices,
        }


@dataclass
class TableType(OptionType):
    _choices: callable
    # allows a updated version of the choices.
    # if choices is all listeners and a new one is added it's not in the choices.
    model: any

    def validate(self, name: str, id_or_name: int | str) -> bool:
        choices = self._choices()
        if str(id_or_name).isdigit():
            object = Session.query(self.model).filter_by(id=id_or_name).first()
            if object not in choices:
                raise ValueError(
                    f"There's no element with the id ({id_or_name}) "
                    f"in the available choices for '{name}'.)"
                )
            return object
        else:
            object = Session.query(self.model).filter_by(name=id_or_name).first()
            if object not in choices:
                raise ValueError(
                    f"There's no element with the name '{id_or_name}' "
                    f"in the available choices for '{name}'.)"
                )
            return object

    def __str__(self) -> str:
        return "table"

    def to_dict(self, commander) -> dict:
        return {"choices": item.to_dict(commander) for item in self._choices()}


@dataclass
class Option:
    """
    The Option class is used to create options for listeners and stagers.

    Args:
        name (str): The name of the option.
        type (OptionType): The type of the option.
        real_name (str): The real name of the option.
        description (str): The description of the option.
        required (bool): If the option is required.
        default (any): The default value of the option.
        editable (bool): If the option is editable.
        render (bool): If the option is rendered in the front-end.
    """

    def __init__(
        self,
        name: str,
        type: OptionType,
        description: str = "",
        required: bool = False,
        editable: bool = True,
        default: any = "",
        real_name: str = "",
        render: bool = True,
    ) -> None:
        self.name = name if name else generate_name()
        self.type = type
        self._real_name = real_name
        self.description = description
        self.required = required
        self.editable = editable
        self._default = default
        self.render = render

    @property
    def default(self) -> any:
        return self._default() if callable(self._default) else self._default

    @property
    def real_name(self) -> str:
        """Returns the name used in the database."""
        return self._real_name if self._real_name else self.name.lower()

    def validate_data(self, data: any) -> OptionType.data_type:
        """Validates the data and if a default value is set it returns it."""
        if not data:
            if self.required and self.default is None:
                raise ValueError(f"{self.name} is required.")
            return self.default

        if type(data) != self.type.data_type and type(self.type) not in (
            BooleanType,
            ChoiceType,
            TableType,
        ):
            try:
                data = self.type.data_type(data)
            except ValueError:
                raise TypeError(
                    f"{self.name} has to be a type of '{self.type.data_type.__name__}'."
                )

        data = self.type.validate(self.name, data)
        return data

    def to_dict(self, commander: "Commander") -> dict:
        data = {
            "name": self.name,
            "real_name": self.real_name,
            "type": str(self.type),
            "type_data": self.type.to_dict(commander),
            "required": self.required,
            "description": self.description,
            "default": self.default,
            "editable": self.editable,
            "render": self.render,
        }
        return data

    def __repr__(self) -> str:
        return f"<Option(name={self.name}, type={self.type})>"


@dataclass
class OptionPool:
    """Used to store options for a Class"""

    options: list[Option] = field(default_factory=list)

    def register_option(self, option: Option):
        """Register a new option"""
        self.options.append(option)

    def get_option(self, real_name: str) -> Option:
        """Get an option by real name"""
        for option in self.options:
            if option.real_name == real_name:
                return option
        raise ValueError(f"The option '{real_name}' doesn't exist.")

    def validate(self, real_name: str, value: any) -> any:
        """Validate data for an option"""
        option = self.get_option(real_name)
        return option.validate_data(value)

    def validate_all(self, data: dict, edit: bool = False) -> dict:
        """Validate all options using the data"""
        cleaned_data = {}
        for option in self.options:
            if option.real_name not in data and edit:
                continue
            value = data.get(option.real_name, "")
            cleaned_data[option.real_name] = option.validate_data(value)
        return cleaned_data

    def to_dict(self, commander: "Commander") -> list:
        return [option.to_dict(commander) for option in self.options]

    def extend(self, option_pool: "OptionPool"):
        self.options.extend(option_pool.options)


class DefaultListenerPool(OptionPool):
    """Contains all default options for a listener."""

    def __init__(self, added_options: list[Option] = []):
        super().__init__()
        self.options = [
            Option(
                name="Name",
                description="The name of the listener.",
                type=StringType(),
                required=True,
                default=lambda: generate_name(),
            ),
            Option(
                name="Address",
                description="The address the listener should listen on.",
                type=AddressType(),
                required=True,
                default="0.0.0.0",
            ),
            Option(
                name="Port",
                description="The port the listener should listen on.",
                type=PortType(),
                required=True,
                default=9999,
            ),
            Option(
                name="SSL",
                description="If the listener should use SSL.",
                type=BooleanType(),
                default=True,
            ),
            Option(
                name="Enabled",
                description="If the listener should be enabled on startup.",
                type=BooleanType(),
                default=True,
            ),
            Option(
                name="Connection limit",
                real_name="limit",
                description="How many devices can be connected at the same time",
                type=IntegerType(),
                default=5,
            ),
            Option(
                name="Response timeout",
                real_name="timeout",
                description="How long the listener should wait for a"
                " response before marking the device as offline.",
                type=IntegerType(),
                default=10,
            ),
        ]
        self.options.extend(added_options)


class DefaultStagerPool(OptionPool):
    """Contains all default options for a stager."""

    def __init__(self, added_options: list[Option] = [], payloads: list[str] = []):
        super().__init__()
        self.options = [
            Option(
                name="Name",
                description="The name of the stager.",
                type=StringType(),
                required=True,
                default=lambda: generate_name(),
            ),
            Option(
                name="Listener",
                description="The listener, the stager should connect to.",
                type=TableType(
                    lambda: Session.query(ListenerModel).all(), ListenerModel
                ),
                required=True,
                default=1,
                editable=False,
                render=False,
            ),
            Option(
                name="Retries",
                description="How often the stager should try to connect, "
                "before it will exit.",
                type=IntegerType(),
                default=200,
            ),
            Option(
                name="Delay",
                description="The delay before the stager should connect to the server.",
                type=IntegerType(),
                default=1,
            ),
            Option(
                name="Different address/domain",
                real_name="different_address",
                description="Use a different address/domain then specified "
                "by the listener to connect to.",
                type=AddressType(),
                required=False,
            ),
        ]
        self.options.extend(added_options)
        self.options.append(
            Option(
                name="Payload",
                description="The payload to use",
                real_name="payload",
                type=ChoiceType(payloads, str),
                default="python",
                required=True,
                render=False,
                editable=False,
            )
        )
