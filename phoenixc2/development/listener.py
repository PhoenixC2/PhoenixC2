from phoenixc2.server.commander import Commander
from phoenixc2.server.database.listeners import ListenerModel
from phoenixc2.server.kits.base_listener import BaseListener
from phoenixc2.server.utils.misc import generate_name
commander = Commander()
def generate_listener(
    listener: BaseListener
) -> ListenerModel:
    """Generate a listener based on the listener model"""
    return ListenerModel(
        name=generate_name(),
        
