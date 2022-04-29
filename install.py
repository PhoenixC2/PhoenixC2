import os
import shutil
from hashlib import md5
import sqlite3
import random
import importlib
import string
import subprocess
path = "/usr/share/Phoenix-Framework/"
if os.getuid() != 0:
    print("[ERROR] Please start with Sudo or Root Rights")
    exit()
print("[INFO] Starting Setup")

print("[INFO] Install Python Modules")
os.system("pip3 install -r requirements.txt -q")

print("[INFO] Creating Directory")
shutil.copytree(os.getcwd() + "/Phoenix-Framework", path)

print("[INFO] Creating Database")
conn = sqlite3.connect(path + "Data/db.sqlite3")
curr = conn.cursor()
curr.execute("CREATE TABLE IF NOT EXISTS Users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, admin INTEGER);")
curr.execute("CREATE TABLE IF NOT EXISTS Devices (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, Hostname TEXT, Address VARCHAR(20), Connection_Date DATE, Last_Online DATE);")
curr.execute("CREATE TABLE IF NOT EXISTS Listeners (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, Name TEXT, Type TEXT, Config TEXT);")
curr.execute("CREATE TABLE IF NOT EXISTS Stagers (Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, Name TEXT, ListenerId INTEGER)")
conn.commit()

print("[INFO] Creating Admin User")
username = "Phoenix"
password = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
hashed_password = md5(password.encode()).hexdigest()
curr.execute(f"INSERT INTO Users (username, password, admin) VALUES ('phoenix', '{hashed_password}', 1);")
conn.commit()
print("[SUCCESS] Admin User Created")
print(f"Credentials: {username}:{password}")

print("[INFO] Copying Binaries")
binaries = ["pfserver", "pfclient", "pfcreate"]
for binary in binaries:
    shutil.copy(os.getcwd() + "/Phoenix-Framework/" + binary, "/usr/bin/" + binary)
    os.system("chmod +x /usr/bin/" + binary)
print("[SUCCESS] Binaries Copied")


print("[INFO] Generating SSL Certificates")
country = "".join(random.choices(string.ascii_uppercase + string.digits, k=2))
state = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
city = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
org = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
org_unit = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
common_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
subprocess.run(["openssl", "req", "-x509", "-nodes", "-days", "365", "-newkey", "rsa:2048", "-keyout", path + "Data/ssl.key", "-out", path + "Data/ssl.pem", "-subj", f"/C={country}/ST={state}/L={city}/O={org}/OU={org_unit}/CN={common_name}"], shell=False)
print("[SUCCESS] Setup Complete")