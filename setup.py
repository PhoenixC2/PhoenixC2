import os
import sqlite3
path = "/usr/share/Phoenix-Framework/"
if os.getuid() != 0:
    print("[ERROR] Please start with Sudo or Root Rights")
    exit()
print("[INFO] Starting Setup")
print("[INFO] Install Python Modules")
try:
    import flask
except:
    os.system("pip install flask -U -q")
try:
    import cryptography
except:
    os.system("pip install cryptography -U -q")
print("Setting Up Configs")
os.mkdir(path)
conn = sqlite3.connect(path + "db.sqlite3")
curr = conn.cursor()