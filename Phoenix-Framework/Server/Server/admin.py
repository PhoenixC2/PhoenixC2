import string
import random
import subprocess
from Database import *
from Database.base import Base


def create_super_user():
    """Create the head admin."""
    print("[INFO] Creating admin.")

    existing_admin = db_session.query(UserModel).first()
    if existing_admin is not None:
        print("[INFO] Deleting old admin.")
        db_session.delete(existing_admin)

    password = "".join(random.choice(string.ascii_letters + string.digits)
                       for _ in range(10))
    admin = UserModel(
        username="phoenix",
        admin=True,
    )
    admin.set_password(password)
    db_session.add(admin)
    db_session.commit()
    print("[SUCCESS] Admin user created.")
    print(f"Credentials: phoenix:{password}")


def generate_database():
    """Create the database."""
    print("[INFO] Creating Database")
    Base.metadata.create_all(engine)


def generate_ssl(path: str):
    """Generate the ssl certificates."""
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
    subprocess.run(["openssl", "req", "-x509", "-nodes", "-days", "365", "-newkey", "rsa:2048", "-keyout", path + "Data/ssl.key",
                    "-out", path + "Data/ssl.pem", "-subj", f"/C={country}/ST={state}/L={city}/O={org}/OU={org_unit}/CN={common_name}"], shell=False)
    print("[SUCCESS] Generated SSL certificates.")


def backup_database():
    """Backup the database."""
    ...


def promote_to_main():
    """Promote the Server to a main server."""
    ...


def degrade_to_sub():
    """Degrade the server to a sub server."""
    ...


def reset_database():
    """Reset the database."""
    ...


def reset_table(table: str):
    """Reset a table."""
    model = {
        "users": UserModel,
        "listeners": ListenerModel,
        "stagers": StagerModel,
        "credentials": CredentialModel,
        "operations": OperationModel,
        "devices": DeviceModel,
        "logs": LogEntryModel

    }[table]
    for entry in db_session.query(model).all():
        db_session.delete(entry)
    db_session.commit()
