import os
import random
import string
import subprocess

from sqlalchemy import inspect

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
from phoenix_framework.server.utils.config import load_config
from phoenix_framework.server.utils.resources import get_resource
from phoenix_framework.server.utils.ui import log

DIRECTORIES = ["stagers", "downloads", "uploads", "pictures"]


def generate_database():
    """Create the database."""
    log("Creating database", "info")
    Base.metadata.create_all(engine)
    log("Created the database.", "success")


def backup_database():
    """Backup the database."""
    ...


def check_for_super_user():
    """Return if the server has an admin user."""
    try:
        return Session.query(UserModel).first() is not None
    except Exception:
        return False


def check_for_directories():
    """Return if the server has the directories."""
    return all(
        [
            os.path.exists(str(get_resource("data", dir, skip_file_check=True)))
            for dir in DIRECTORIES
        ]
    )


def check_for_ssl():
    """Return if the server has ssl certificates."""
    return all(
        [
            os.path.exists(str(get_resource("data", dir, skip_file_check=True)))
            for dir in ["ssl.pem", "ssl.key"]
        ]
    )


def check_for_database():
    """Return if the database exists."""
    config = load_config()
    # check if all the tables exist
    return all(
        [
            table in inspect(engine).get_table_names()
            for table in Base.metadata.tables.keys()
        ]
    )


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
    log(f"Resetting {table}", "info")
    Base.metadata.drop_all(engine, [models[table].__table__])
    Base.metadata.create_all(engine, [models[table].__table__])
    log(f"Reset {table}", "success")
    Session.remove()


def recreate_super_user():
    """Recreate the head admin."""
    existing_admin: UserModel = Session.query(UserModel).first()
    if existing_admin is not None:
        log("Deleting current admin.", "info")
        existing_admin.delete(Session)
        log("Deleted current admin.", "success")
    log("Creating new admin", "info")
    password = "".join(
        random.choice(string.ascii_letters + string.digits + string.punctuation)
        for _ in range(10)
    )
    admin = UserModel(id=1, username="phoenix", admin=True)
    admin.generate_api_key()
    admin.set_password(password)
    Session.add(admin)
    Session.commit()
    log("Admin user recreated.", "success")
    log(f"Credentials: phoenix:{password}", "info")
    log(f"API Key: '{admin.api_key}'", "info")
    Session.remove()


def reset_server(reset: bool = False):
    """Reset the server to the default state."""
    if reset:
        log("Resetting server", "critical")
    else:
        log("Setting up the server.", "info")
    if not check_for_directories() or reset:
        reset_directories()
    if not check_for_ssl() or reset:
        regenerate_ssl()
    if not check_for_database() or reset:
        generate_database()
    if not check_for_super_user() or reset:
        recreate_super_user()

    if reset:
        log("Reset finished.", "success")
    else:
        log("Setup finished.", "success")


def check_for_setup():
    """Return if the server has been setup."""
    return all(
        [
            check_for_super_user(),
            check_for_directories(),
            check_for_ssl(),
            check_for_database(),
        ]
    )
