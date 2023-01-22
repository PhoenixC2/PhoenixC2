from phoenixc2.server.commander import Commander
from phoenixc2.server.database import ListenerModel
from phoenixc2.server.kits.base_listener import BaseListener
from phoenixc2.server.utils.misc import generate_name

commander = Commander()


def generate_listener(
    type: BaseListener,
    options: dict = None,
) -> ListenerModel:
    """Generate a listener based on the listener model

    Args:
    -----
        type (BaseListener): The listener type
        options (dict): The options for the listener

    Returns:
    --------
        ListenerModel: The listener model
    """
    return ListenerModel(name=generate_name(), type=type.name, options=options)
