import os

from pystyle import Add, Box, Colorate, Colors
from rich.console import Console

# logo
logo = Add.Add("""
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

""", f"""

   ▄███████▄    ▄█    █▄     ▄██████▄     ▄████████ ███▄▄▄▄    ▄█  ▀████    ▐████▀ 
  ███    ███   ███    ███   ███    ███   ███    ███ ███▀▀▀██▄ ███    ███▌   ████▀  
  ███    ███   ███    ███   ███    ███   ███    █▀  ███   ███ ███▌    ███  ▐███    
  ███    ███  ▄███▄▄▄▄███▄▄ ███    ███  ▄███▄▄▄     ███   ███ ███▌    ▀███▄███▀    
▀█████████▀  ▀▀███▀▀▀▀███▀  ███    ███ ▀▀███▀▀▀     ███   ███ ███▌    ████▀██▄     
  ███          ███    ███   ███    ███   ███    █▄  ███   ███ ███    ▐███  ▀███    
  ███          ███    ███   ███    ███   ███    ███ ███   ███ ███   ▄███     ███▄  
 ▄████▀        ███    █▀     ▀██████▀    ██████████  ▀█   █▀  █▀   ████       ███▄
{Box.DoubleCube("Made by Screamz2k")}""", 4, True)

console = Console()


def log(text: str, alert: str=""):
    """Log important information to the console"""
    if os.getenv("PHOENIX_LOG") == "false":
        return
    style = ""
    if alert == "info":
        style = "blue"
    elif alert == "success":
        style = "green"
    elif alert == "warning":
        style = "yellow"
    elif alert == "error":
        style = "red"
    elif alert == "critical":
        style = "#9e0909"
    console.print("[" + alert.upper() + "] " + text, style=style)


def ph_print(text: str, force: bool = False):
    """Print phoenix-styled text to the console"""
    if os.getenv("PHOENIX_LOG") == "false" and not force:
        return
    print(Colorate.Horizontal(Colors.yellow_to_red, text))
