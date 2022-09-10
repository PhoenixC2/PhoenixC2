import os
import shutil
import importlib
import random
import string
import subprocess
import argparse
import uuid

def check_uid():
    """Check if user is root"""

    if os.getuid() != 0:
        print("[ERROR] Please start with sudo or Root rights.")
        exit(1)


def uninstall(path: str):
    """Uninstall the Framework"""
    os.system(f"rm -rf {path}")
    os.system("rm /usr/bin/pfserver")
    os.system("rm /usr/bin/pfclient")


def create_main_folder(path: str):
    """Create and copy all files to the main folder"""
    print(path)
    print(os.getcwd() + "/Phoenix-Framework/")
    print("[INFO] Copying files.")
    shutil.copytree(os.getcwd() + "/Phoenix-Framework/",
                    path + ".")
    print("[SUCCESS] Copied files.")


def install_requirements():
    global sqlalchemy, sessionmaker
    """Install pip requirements"""
    print("[INFO] Installing python modules.")
    os.system("pip3 install -r requirements.txt -q")
    print("[SUCCESS] Installed python modules.")
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker


def copy_binaries():
    """Copy the binaries"""
    print("[INFO] Copying binaries.")
    binaries = ["pfserver", "pfclient"]
    for binary in binaries:
        shutil.copy(os.getcwd() + "/Phoenix-Framework/" +
                    binary, "/usr/bin/" + binary)
        os.system("chmod +x /usr/bin/" + binary)
    print("[SUCCESS] Binaries copied.")


def generate_ssl(path: str):
    """Generate the ssl certificates"""
    print("[INFO] Generating SSL certificates.")
    country = "".join(random.choices(
        string.ascii_uppercase + string.digits, k=2))
    state = "".join(random.choices(
        string.ascii_uppercase + string.digits, k=10))
    city = "".join(random.choices(
        string.ascii_uppercase + string.digits, k=10))
    org = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    org_unit = "".join(random.choices(
        string.ascii_uppercase + string.digits, k=10))
    common_name = "".join(random.choices(
        string.ascii_uppercase + string.digits, k=10))
    subprocess.run(["openssl", "req", "-x509", "-nodes", "-days", "365", "-newkey", "rsa:2048", "-keyout", path + "/Server/Data/ssl.key",
                    "-out", path + "/Server/Data/ssl.pem", "-subj", f"/C={country}/ST={state}/L={city}/O={org}/OU={org_unit}/CN={common_name}"], shell=False)
    print("[SUCCESS] Generated SSL certificates.")


def create_connection(path: str):
    global Database, engine, db_session
    """Create the database connection"""
    Database = importlib.import_module("Phoenix-Framework.Server.Database")
    engine = sqlalchemy.create_engine(
        f"sqlite:///{path}/Server/Data/db.sqlite3")
    db_session = sessionmaker(bind=engine)()


def create_database():
    """Create the database"""
    print("[INFO] Creating Database")
    Base = Database.base.Base
    Base.metadata.create_all(engine)


def create_super_user():
    """Create the head admin"""
    print("[INFO] Creating admin.")

    existing_admin = db_session.query(Database.UserModel).first()
    if existing_admin is not None:
        print("[INFO] Deleting old admin.")
        db_session.delete(existing_admin)

    password = "".join(random.choice(string.ascii_letters + string.digits)
                       for _ in range(10))
    admin = Database.UserModel(
        username="phoenix",
        admin=True,
        api_key=str(uuid.uuid1())
    )
    admin.set_password(password)
    db_session.add(admin)
    db_session.commit()
    print("[SUCCESS] Admin user created.")
    print(f"Credentials: phoenix:{password}")


parser = argparse.ArgumentParser(
    "install.py", "sudo install.py", "Install, modify or remove the Phoenix-Framework.")
parser.add_argument("-l", "--location", help="The install location.",
                    default="/usr/share/Phoenix-Framework/")
parser.add_argument(
    "-r", "--remove", help="Remove the framework :(", action="store_true")
if __name__ == "__main__":
    args = parser.parse_args()
    check_uid()
    if args.remove:
        if input("Are you sure you want to remove the Framework [Y/n]: ").lower() in ["y", "yes"]:
            uninstall(args.location)
            print("Uninstalled.")
            exit()
    print("[INFO] Starting Setup")

    install_requirements()
    create_main_folder(args.location)
    copy_binaries()
    create_connection(args.location)
    create_database()
    create_super_user()
    generate_ssl(args.location)
    print("[SUCCESS] Setup Complete")
