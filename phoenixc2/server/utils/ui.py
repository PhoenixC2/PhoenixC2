import os
from typing import TYPE_CHECKING

from pystyle import Add, Box, Colorate, Colors
from rich.console import Console

if TYPE_CHECKING:
    from phoenixc2.server.database import DeviceModel
# logo
logo = Add.Add(
    """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣈⠀⠀⠀⠀⠀⢀⣬⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣨⣿⠀⠀⠀⠀⣬⣿⣯⣮⣌⣌⣌⢌⢈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣨⣿⣿⠀⠀⠀⣸⣿⣿⠁⠀⠐⠑⠑⠳⡳⣷⣮⢌⠈⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⠀⠀⢀⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠐⠳⣷⣎⠈⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣰⠈⠀⠀⣰⣿⣿⣿⠌⠀⣰⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⣿⢎⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣼⢏⠀⠀⡰⣿⣿⣿⣏⠀⠐⣿⣿⣏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⣷⢎⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣷⣿⠌⠀⠀⣳⣿⣿⣿⢎⠀⡱⣿⣿⠌⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⣿⠎⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⢎⠀⠀⡳⣿⣿⣿⣎⠈⠱⣷⣯⠈⠀⠀⢀⠈⠀⠀⠀⠀⠀⠀⠀⠀⣱⣯⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡳⣿⣿⣯⢌⠈⠱⣷⣿⣿⣿⣎⢌⠘⠱⠀⠀⢈⣯⢌⠀⠀⠀⠀⠀⠀⠀⣰⣿⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡀⠈⠀⠐⡳⣷⣿⣿⣯⣎⣽⣿⣿⣿⣿⣿⣿⣮⣮⣿⣿⣿⣏⠀⠀⠀⠀⠀⠀⣰⣿⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠱⣧⣮⣌⣌⢈⢙⢙⢹⣿⣿⣿⣿⣿⣿⡿⠳⠑⠁⠀⠑⠱⠀⠀⠀⠀⠀⠀⣾⠟⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠰⣿⢿⠳⡷⡷⣿⣿⣿⣿⣿⣿⣿⠓⣈⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡿⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⣷⣎⠀⠀⠀⠀⠀⣼⣿⣿⠟⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⡿⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⡳⣯⢌⠀⠀⠀⣿⣿⣿⣯⠀⣳⣏⠀⠀⠀⠀⠀⠀⢀⣬⣿⠗⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⡳⣷⣎⣌⣿⣿⣿⣿⣏⠈⠱⣧⣌⠈⢈⣈⣮⡿⠓⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠱⡳⡷⣷⣿⣿⣯⣮⣾⡿⡷⠳⠓⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

""",
    f"""

   ▄███████▄    ▄█    █▄     ▄██████▄     ▄████████ ███▄▄▄▄    ▄█  ▀████    ▐████▀ 
  ███    ███   ███    ███   ███    ███   ███    ███ ███▀▀▀██▄ ███    ███▌   ████▀  
  ███    ███   ███    ███   ███    ███   ███    █▀  ███   ███ ███▌    ███  ▐███    
  ███    ███  ▄███▄▄▄▄███▄▄ ███    ███  ▄███▄▄▄     ███   ███ ███▌    ▀███▄███▀    
▀█████████▀  ▀▀███▀▀▀▀███▀  ███    ███ ▀▀███▀▀▀     ███   ███ ███▌    ████▀██▄     
  ███          ███    ███   ███    ███   ███    █▄  ███   ███ ███    ▐███  ▀███    
  ███          ███    ███   ███    ███   ███    ███ ███   ███ ███   ▄███     ███▄  
 ▄████▀        ███    █▀     ▀██████▀    ██████████  ▀█   █▀  █▀   ████       ███▄
{Box.DoubleCube("Made by Screamz2k")}""",
    4,
    True,
)

console = Console()


def log(text: str, alert: str = ""):
    """Log important information to the console"""
    if os.getenv("PHOENIX_LOG", "") == "false":
        return
    style = ""
    if alert == "info":
        style = "blue"
    elif alert == "success":
        style = "green"
    elif alert == "warning":
        style = "yellow"
    elif alert == "danger":
        style = "red"
    elif alert == "critical":
        style = "#ff0000"
    console.print("[" + alert.upper() + "] " + text, style=style)


def ph_print(text: str, force: bool = False):
    """Print phoenix-styled text to the console"""
    if os.getenv("PHOENIX_LOG", "") == "false" and not force:
        return
    print(Colorate.Horizontal(Colors.yellow_to_red, text))


def log_connection(device: "DeviceModel", reconnect: bool = False):
    from phoenixc2.server.database import LogEntryModel

    """Log the new connection to the console and database"""
    if reconnect:
        status = f"Device '{device.hostname}' ({device.address}) reconnected to the server. [{device.name}]"
    else:
        status = f"New device '{device.hostname}' ({device.address}) connected to the server. [{device.name}]"
    ph_print(status)
    LogEntryModel.log(
        "success",
        "devices",
        f"Device '{device.name}' connected to '{device.name}'.",
        log_to_cli=False,
    )
