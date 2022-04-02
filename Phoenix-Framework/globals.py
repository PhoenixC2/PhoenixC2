# libraries
import click
import base64
import subprocess
import json
import logging
from sqlite3 import connect, OperationalError
import socket
from flask import Flask, Blueprint, request, jsonify, render_template, redirect, url_for, send_from_directory
import os
from rich.console import Console
import time
from pystyle import *
from rich.progress_bar import ProgressBar
import threading
from cryptography.fernet import Fernet, InvalidToken
from argparse import ArgumentParser

# logo
logo = Add.Add("""⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
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

# Objects
console = Console()
logging.basicConfig(filename='phoenix.log', encoding='utf-8', level=logging.ERROR)
# disable flask logging
logging.getLogger('werkzeug').disabled = True
# methods 
def log(text, alert=""):
    style = ""
    # log type is choosen by alert
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


def ph_print(text):
    print(Colorate.Horizontal(Colors.yellow_to_red, text))