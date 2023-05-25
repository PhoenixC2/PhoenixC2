"""This is the C2 commander class which handles the devices & listeners"""
from multiprocessing import Process
from threading import Thread
from typing import Optional, TYPE_CHECKING
from flask import Flask
from phoenixc2.server.kits.handler_base import BaseHandler
from phoenixc2.server.kits.listener_base import BaseListener
from phoenixc2.server.plugins.base import (
    BasePlugin,
    BlueprintPlugin,
    ExecutedPlugin,
    RoutePlugin,
    PolyPlugin,
    ConnectionEventPlugin,
)
from phoenixc2.server.utils.web import FlaskThread
from phoenixc2.server.utils.misc import Status
from phoenixc2.server.utils.ui import log_connection, log

if TYPE_CHECKING:
    from phoenixc2.server.database import DeviceModel
INVALID_ID = "Invalid ID"
HANDLER_DOES_NOT_EXIST = "Handler doesn't exist"
LISTENER_DOES_NOT_EXIST = "Listener doesn't exist"


class Commander:
    """This is the Commander is used as a registry for all devices and listeners"""

    def __init__(self):
        self.api_thread: FlaskThread
        self.api: Flask
        self.active_listeners: dict[int, BaseListener] = {}
        self.active_handlers: dict[int, BaseHandler] = {}
        self.active_plugins: dict[str, BasePlugin] = {}
        self.connection_event_plugins: list[tuple[ConnectionEventPlugin, dict]] = []

    def get_active_handler(self, handler_id: int) -> Optional[BaseHandler]:
        """Get a handler by id"""
        try:
            return self.active_handlers[int(handler_id)]
        except ValueError as e:
            raise ValueError(INVALID_ID) from e
        except KeyError as e:
            raise KeyError(HANDLER_DOES_NOT_EXIST) from e

    def get_active_listener(self, listener_id: int) -> Optional[BaseListener]:
        """Get a listener by id"""
        try:
            return self.active_listeners[int(listener_id)]
        except ValueError as e:
            raise ValueError(INVALID_ID) from e
        except KeyError:
            raise KeyError(LISTENER_DOES_NOT_EXIST) from None

    def add_active_listener(self, listener: BaseListener):
        """Add a listener to the commander"""
        self.active_listeners[int(listener.id)] = listener

    def add_active_handler(self, handler: BaseHandler):
        """Add a handler to the commander"""
        self.active_handlers[int(handler.id)] = handler

    def remove_active_listener(self, listener_id: int):
        """Remove a listener from the commander"""
        try:
            self.active_listeners.pop(int(listener_id))
        except ValueError as e:
            raise ValueError(INVALID_ID) from e
        except KeyError as e:
            raise KeyError(LISTENER_DOES_NOT_EXIST) from e

    def remove_active_handler(self, handler_id: int):
        """Remove a device from the commander by id"""
        try:
            self.active_handlers.pop(int(handler_id))
        except ValueError as e:
            raise ValueError(INVALID_ID) from e
        except KeyError as e:
            raise KeyError(HANDLER_DOES_NOT_EXIST) from e

    def load_plugin(self, plugin: BasePlugin, config: dict):
        """Load a plugin"""
        if not plugin.check_dependencies():
            if (
                input(
                    f"Plugin {plugin.name} has missing dependencies."
                    "Would you like to install them? (y/n): "
                ).lower()
                == "y"
            ):
                plugin.install_dependencies()
            else:
                raise ModuleNotFoundError(
                    f"Plugin {plugin.name} has missing dependencies"
                )
        if plugin.name in self.active_plugins:
            raise KeyError(f"Plugin {plugin.name} already loaded")

        if issubclass(plugin, ExecutedPlugin):
            try:
                if plugin.execution_type == "direct":
                    plugin.execute(self, config)
                elif plugin.execution_type == "thread":
                    Thread(
                        target=plugin.execute, args=(self, config), name=plugin.name
                    ).start()
                elif plugin.execution_type == "process":
                    Process(
                        target=plugin.execute, args=(self, config), name=plugin.name
                    ).start()
                else:
                    raise ValueError(f"Invalid execution type {plugin.execution_type}")
            except Exception as e:
                raise Exception(f"Failed to load plugin '{plugin.name}'") from e

        elif issubclass(plugin, BlueprintPlugin):
            blue_print = plugin.execute(self, config)
            self.api.register_blueprint(blue_print, url_prefix=blue_print.url_prefix)

        elif issubclass(plugin, RoutePlugin):
            self.api.add_url_rule(plugin.rule, plugin.name, plugin.execute)

        elif issubclass(plugin, ConnectionEventPlugin):
            self.connection_event_plugins.append((plugin, config))

        elif issubclass(plugin, PolyPlugin):
            # Loads all plugins which are specified by the poly-plugin
            for sub_plugin in plugin.plugins:
                self.load_plugin(sub_plugin, config)

        else:
            plugin.execute(self, config)

        self.active_plugins[plugin.name] = plugin

    def new_connection(self, device: "DeviceModel", reconnect: bool = False):
        """Called when a new device connects"""
        log_connection(device, reconnect)

        # run connection event plugins
        for plugin, config in self.connection_event_plugins:
            try:
                plugin.execute(device, config)
            except Exception as e:
                log(
                    f"Failed to execute connection event plugin {plugin.name}: {e}",
                    Status.Danger,
                )
