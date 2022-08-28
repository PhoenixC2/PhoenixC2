import os
import sys
import shutil
import importlib
import random
import string
import subprocess
if os.getuid() != 0:
    print("[ERROR] Please start with Sudo or Root Rights")
    exit()
if len(sys.argv) == 1:
    path = "/usr/share/"
else:
    path = sys.argv[1]

print("[INFO] Starting Setup")

if not os.path.exists(path):
    print("[INFO] Creating Directory")
    os.makedirs(path)

print("[INFO] Install Python Modules")
os.system("pip3 install -r requirements.txt -q")

print("[INFO] Copying Files")
shutil.copytree(os.getcwd() + "/Phoenix-Framework", path + "/Phoenix-Framework")

print("[INFO] Creating Database")
# Imports after sqlalchemy is installed
Database = importlib.import_module("Phoenix-Framework.Database")
sqlalchemy = importlib.import_module("sqlalchemy")
sessionmaker = sqlalchemy.orm.sessionmaker
engine = sqlalchemy.create_engine(f"sqlite:///{path}/Phoenix-Framework/Data/db.sqlite3")
db_session = sessionmaker(bind=engine)()
Base = Database.base.Base
Base.metadata.create_all(engine)
print("[INFO] Creating Admin User")
username = "Phoenix"
password = "".join(random.choice(string.ascii_letters + string.digits)
                   for _ in range(10))

admin = Database.UserModel(
    username=username,
    admin=True,
)
admin.set_password(password)
db_session.add(admin)
db_session.commit()
print("[SUCCESS] Admin User Created")
print(f"Credentials: {username}:{password}")

print("[INFO] Copying Binaries")
binaries = ["pfserver", "pfclient"]
for binary in binaries:
    shutil.copy(os.getcwd() + "/Phoenix-Framework/" +
                binary, "/usr/bin/" + binary)
    os.system("chmod +x /usr/bin/" + binary)
    os.remove(path + "/Phoenix-Framework/" + binary)
print("[SUCCESS] Binaries Copied")


print("[INFO] Generating SSL Certificates")
country = "".join(random.choices(string.ascii_uppercase + string.digits, k=2))
state = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
city = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
org = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
org_unit = "".join(random.choices(
    string.ascii_uppercase + string.digits, k=10))
common_name = "".join(random.choices(
    string.ascii_uppercase + string.digits, k=10))
subprocess.run(["openssl", "req", "-x509", "-nodes", "-days", "365", "-newkey", "rsa:2048", "-keyout", path + "Data/ssl.key",
               "-out", path + "Data/ssl.pem", "-subj", f"/C={country}/ST={state}/L={city}/O={org}/OU={org_unit}/CN={common_name}"], shell=False)
print("[SUCCESS] Setup Complete")
