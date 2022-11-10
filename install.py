import argparse
import importlib
import os
import random
import shutil
import string
import subprocess
import sys
import uuid

parser = argparse.ArgumentParser(
    "install.py", "sudo install.py", "Install, modify or remove the Phoenix-Framework."
)
parser.add_argument("--remove", help="Remove the framework :(", action="store_true")
parser.add_argument("--update", help="Update the framework", action="store_true")
parser.add_argument(
    "-p",
    "--password",
    help="The password to use for the super user account instead of a random one.",
    default="",
)


def create_venv(path: str):
    """Create the virtual environment"""
    print("[INFO] Creating virtual environment.")
    os.system(f"python3 -m venv {path}/venv")
    print("[SUCCESS] Created virtual environment.")
    # activate venv
    os.system(f"source {path}/venv/bin/activate")
    print("[SUCCESS] Activated virtual environment.")


def run_setup():
    """Run the setup"""
    print("[INFO] Installing package.")
    os.system("python -m pip install .")
    print("[SUCCESS] Installed package.")


def generate_ssl(path: str):
    """Generate the ssl certificates"""
    print("[INFO] Generating SSL certificates.")
    country = "".join(random.choices(string.ascii_uppercase + string.digits, k=2))
    state = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    city = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    org = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    org_unit = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    common_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-nodes",
            "-days",
            "365",
            "-newkey",
            "rsa:2048",
            "-keyout",
            path + "/Server/Data/ssl.key",
            "-out",
            path + "/Server/Data/ssl.pem",
            "-subj",
            f"/C={country}/ST={state}/L={city}/O={org}/OU={org_unit}/CN={common_name}",
        ],
        shell=False,
    )
    print("[SUCCESS] Generated SSL certificates.")


def create_config(path: str):
    """Create the config file"""
    print("[INFO] Creating config file.")
    with open(os.getcwd() + "Server/Data/config.toml") as f:
        config = f.read()


def create_database():
    """Create the database"""
    print("[INFO] Creating Database")
    Base = Database.base.Base
    Base.metadata.create_all(engine)


def remove():
    """Remove the framework"""
    os.system("python -m pip uninstall Phoenix-Framework")


def update():
    """Update the framework"""
    os.system("python -m pip install Phoenix-Framework --upgrade")


if __name__ == "__main__":
    args = parser.parse_args()
    if args.remove:
        if input("Are you sure you want to remove the Framework [Y/n]: ").lower() in [
            "y",
            "yes",
        ]:
            remove()
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
