import os
import shutil
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
shutil.copytree(os.getcwd() + "/Phoenix-Framework", path)
conn = sqlite3.connect(path + "Data/db.sqlite3")
curr = conn.cursor()
curr.execute("CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT, admin INTEGER)")
curr.execute("CREATE TABLE IF NOT EXISTS Devices (id INTERGER PRIMARY KEY, Hostname TEXT, Address VARCHAR(20), Connection_Date VARCHAR(20), Last_Online VARCHAR(20));")
conn.commit()
conn.close()
print("[INFO] Setup Complete")
