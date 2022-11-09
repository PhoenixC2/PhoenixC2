import os
import random
import string
import subprocess
from uuid import uuid1

from phoenix_framework.server.database import (
    CredentialModel,
    DeviceModel,
    ListenerModel,
    LogEntryModel,
    OperationModel,
    Session,
    StagerModel,
    TaskModel,
    UserModel,
    engine,
)
from phoenix_framework.server.database.base import Base
from phoenix_framework.server.utils.resources import get_resource
from phoenix_framework.server.utils.ui import log

DIRECTORIES = ["stagers", "downloads", "uploads"]


def regenerate_ssl():
    """Generate the ssl certificates."""
    log("Generating ssl certificates", "info")
    ssl_cert = get_resource("data", "ssl.pem", skip_file_check=True)
    ssl_key = get_resource("data", "ssl.key", skip_file_check=True)

    # check if the ssl certificates exist and delete them
    if os.path.exists(ssl_cert):
        os.remove(ssl_cert)
    if os.path.exists(ssl_key):
        os.remove(ssl_key)
    # quiet mode for openssl
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:4096",
            "-keyout",
            ssl_key,
            "-out",
            ssl_cert,
            "-days",
            "365",
            "-nodes",
            "-subj",
            "/CN=US",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    log("Generated ssl certificates.", "success")


def reset_directories():
    """Delete and recreate the directories for the server where the data is stored."""
    has_to_create = False
    for dir in DIRECTORIES:
        dir = get_resource("data", dir, skip_file_check=True)
        if not os.path.exists(str(dir)):
            has_to_create = True
            os.makedirs(dir)

    if has_to_create:
        log("Created directories.", "success")


def generate_database():
    """Create the database."""
    log("Creating database", "info")
    Base.metadata.create_all(engine)
    log("Created the database.", "success")


def backup_database():
    """Backup the database."""
    ...


def reset_database():
    """Reset the database."""
    Base.metadata.drop_all(engine)
    generate_database()


def reset_table(table: str):
    """Reset a table."""

    models = {
        "users": UserModel,
        "listeners": ListenerModel,
        "stagers": StagerModel,
        "credentials": CredentialModel,
        "operations": OperationModel,
        "devices": DeviceModel,
        "logs": LogEntryModel,
        "tasks": TaskModel,
    }
    if table not in models:
        log(f"{table} doesn't exist.", "error")
        exit(1)
    log(f"Resetting {table}")
    model = models[table]
    count = 0
    for entry in Session.query(model).all():
        Session.delete(entry)
        count += 1
    Session.commit()
    log(f"Deleted {count} columns from {table}.", "success")
    Session.remove()


def recreate_super_user():
    """Recreate the head admin."""
    existing_admin = Session.query(UserModel).first()
    if existing_admin is not None:
        log("Deleting current admin.", "info")
        Session.delete(existing_admin)
        Session.commit()
        log("Deleted current admin.", "success")
    log("Creating new admin", "info")
    password = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(10)
    )
    admin = UserModel(id=1, username="phoenix", admin=True, api_key=str(uuid1()))
    admin.set_password(password)
    Session.add(admin)
    Session.commit()
    log("Admin user recreated.", "success")
    log(f"Credentials: phoenix:{password}", "info")
    Session.remove()


def reset_server(first_time: bool = False):
    """Reset the server to the default state."""
    if first_time:
        log("Setting up the server for the first time.", "info")
    else:
        log("Resetting server", "critical")

    reset_directories()
    regenerate_ssl()
    reset_database()
    recreate_super_user()

    if first_time:
        log("Setup finished.", "success")
    else:
        log("Reset finished.", "success")


def check_for_setup():
    """Return if the server has been setup."""
    return all(
        [
            os.path.exists(str(get_resource("data", dir, skip_file_check=True)))
            for dir in DIRECTORIES + ["ssl.pem", "ssl.key"]
        ]
    )
