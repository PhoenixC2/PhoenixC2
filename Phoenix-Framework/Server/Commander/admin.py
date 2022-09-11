import string
import os
import random
import subprocess
import uuid
from Utils.ui import log
from Database import *
from Database.base import Base


def recreate_super_user():
    """Create the head admin."""
    existing_admin = db_session.query(UserModel).first()
    if existing_admin is not None:
        log("Deleting current admin.", "info")
        db_session.delete(existing_admin)
        db_session.commit()
        log("Deleted current admin.", "success")
    log("Creating new admin", "info")
    password = "".join(random.choice(string.ascii_letters + string.digits)
                       for _ in range(10))
    admin = UserModel(
        id=1,
        username="phoenix",
        admin=True,
        api_key=str(uuid.uuid1())
    )
    admin.set_password(password)
    db_session.add(admin)
    db_session.commit()
    log("Admin user created.", "success")
    log(f"Credentials: phoenix:{password}", "success")


def generate_database():
    """Create the database."""
    log("Creating database", "info")
    Base.metadata.create_all(engine)
    log("Created the database.", "success")


def recreate_ssl(location: str):
    """Generate the ssl certificates."""
    log("Generating SSL certificates.", "info")
    os.remove(location + "/Data/ssl.key")
    os.remove(location + "/Data/ssl.pem")
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
    subprocess.run(["openssl", "req", "-x509", "-nodes", "-days", "365", "-newkey", "rsa:2048", "-keyout", location + "Data/ssl.key",
                    "-out", location + "Data/ssl.pem", "-subj", f"/C={country}/ST={state}/L={city}/O={org}/OU={org_unit}/CN={common_name}"], shell=False)
    log("Generated SSL certificates.", "success")


def backup_database():
    """Backup the database."""
    ...


def promote_to_main():
    """Promote the Server to a main server."""
    ...


def degrade_to_sub():
    """Degrade the server to a sub server."""
    ...


def reset_database(location: str):
    """Reset the database."""
    os.remove(location + "/Data/db.sqlite3")
    generate_database()
    ...


def reset_table(table: str):
    """Reset a table."""
    
    models = {
        "users": UserModel,
        "listeners": ListenerModel,
        "stagers": StagerModel,
        "credentials": CredentialModel,
        "operations": OperationModel,
        "devices": DeviceModel,
        "logs": LogEntryModel

    }
    if table not in models:
        log(f"{table} doesn't exist.", "error")
        exit(1)
    log(f"Resetting {table}")
    model = models[table]
    count = 0
    for entry in db_session.query(model).all():
        db_session.delete(entry)
        count += 1
    db_session.commit()
    log(f"Deleted {count} columns from {table}.", "success")
