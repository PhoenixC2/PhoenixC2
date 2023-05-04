from multiprocessing.util import get_temp_dir
import os
import secrets
import shutil
import imp
import zipfile
import tempfile
import requests

from sqlalchemy import inspect
from OpenSSL import crypto
from phoenixc2.server.database import Session, UserModel, engine
from phoenixc2.server.database.base import Base
from phoenixc2.server.utils.config import load_config, save_config
from phoenixc2.server.utils.resources import get_resource
from phoenixc2.server.utils.ui import log
from phoenixc2.server.utils.misc import Status
from phoenixc2.server.plugins.base import BasePlugin

DIRECTORIES = ["stagers", "downloads", "uploads", "pictures"]


def generate_database(reset: bool = False):
    """Create the database."""
    if reset:
        log("Resetting the database", Status.Info)
        Base.metadata.drop_all(engine)
        log("Reset the database.", Status.Success)

    log("Creating database", Status.Info)
    Base.metadata.create_all(engine)
    log("Created the database.", Status.Success)


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
    load_config()
    # check if all the tables exist
    return all(
        [
            table in inspect(engine).get_table_names()
            for table in Base.metadata.tables.keys()
        ]
    )


def regenerate_ssl():
    """Generate the ssl certificates."""
    log("Generating ssl certificates", Status.Info)
    ssl_cert = get_resource("data", "ssl.pem", skip_file_check=True)
    ssl_key = get_resource("data", "ssl.key", skip_file_check=True)

    # check if the ssl certificates exist and delete them
    if os.path.exists(ssl_cert):
        ssl_cert.unlink()
    if os.path.exists(ssl_key):
        ssl_key.unlink()
    # quiet mode for openssl
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "US"
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, "sha512")
    with open(str(ssl_cert), "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(str(ssl_key), "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))
    log("Generated ssl certificates.", Status.Success)


def reset_directories():
    """Delete and recreate the data directories."""
    has_to_create = False
    for dir in DIRECTORIES:
        dir = get_resource("data", dir, skip_file_check=True)
        if not os.path.exists(str(dir)):
            has_to_create = True
            os.makedirs(dir)

    if has_to_create:
        log("Created directories.", Status.Success)


def reset_table(table: str):
    """Reset a table."""

    # generate models dict from Base
    models = {model.__tablename__.lower(): model for model in Base.__subclasses__()}

    if table not in models:
        log(f"{table} doesn't exist.", Status.Danger)
        exit(1)
    log(f"Resetting {table}", Status.Info)
    Base.metadata.drop_all(engine, [models[table].__table__])
    Base.metadata.create_all(engine, [models[table].__table__])
    log(f"Reset {table}", Status.Success)


def recreate_super_user():
    """Recreate the super user."""
    existing_admin: UserModel = Session.query(UserModel).first()
    if existing_admin is not None:
        log("Deleting current admin.", Status.Info)
        existing_admin.delete()
        log("Deleted current admin.", Status.Success)
    log("Creating new admin", Status.Info)
    password = secrets.token_urlsafe(10)
    admin = UserModel(id=1, username="phoenix", admin=True)
    admin.set_password(password)
    Session.add(admin)
    Session.commit()
    log("Super user recreated.", Status.Success)
    log(f"Credentials: phoenix:{password}", Status.Info)
    log(f"API Key: '{admin._api_key}'", Status.Info)


def setup_server(reset: bool = False):
    """Setup the server or reset it."""
    if reset:
        log("Resetting server", "critical")
    else:
        log("Setting up the server.", Status.Info)
    if not check_for_directories() or reset:
        reset_directories()
    if not check_for_ssl() or reset:
        regenerate_ssl()
    if not check_for_database() or reset:
        generate_database(reset)
    if not check_for_super_user() or reset:
        recreate_super_user()

    if reset:
        log("Reset finished.", Status.Success)
    else:
        log("Setup finished.", Status.Success)


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


def check_plugin(path: str) -> BasePlugin:
    """Check if a plugin is valid."""
    if not os.path.exists(path):
        log("Plugin's path doesn't exist.", Status.Danger)
        exit(1)

    if not os.path.isdir(path):
        log("Plugin is not a directory.", Status.Danger)
        exit(1)

    if not os.path.exists(os.path.join(path, "plugin.py")):
        log("Plugin doesn't have a plugin.py file.", Status.Danger)
        exit(1)

    try:
        return imp.load_module("plugin", *imp.find_module("plugin", [path])).Plugin
    except Exception as e:
        log(f"Error while importing plugin: {e}", Status.Danger)
        exit(1)


def enable_plugin(plugin: BasePlugin):
    """Enable a plugin."""
    config = load_config()
    config["plugins"] = config.get("plugins", {})
    config["plugins"][plugin.name] = {"enabled": True}
    save_config(config)

    log(f"Plugin '{plugin.name}' enabled.", Status.Success)


def add_plugin(path: str):
    """Add a plugin."""
    plugin_dir = get_resource("plugins")

    plugin = check_plugin(path)

    try:
        shutil.copytree(path, os.path.join(plugin_dir, plugin.name))
    except Exception as e:
        log(f"Error while copying plugin: {e}", Status.Danger)
        exit(1)

    log(f"Plugin '{plugin.name}' added.", Status.Success)

    enable_plugin(plugin)

    return plugin


def add_plugin_zip(path: str):
    """Add a plugin zip."""
    temp_plugin_dir = os.path.join(tempfile.gettempdir(), "phoenix_plugin")

    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(temp_plugin_dir)

    add_plugin(temp_plugin_dir)


def add_plugin_zip_url(url: str):
    """Add a plugin zip url."""

    try:
        r = requests.get(url)
        with open(os.path.join(get_temp_dir(), "plugin.zip"), "wb") as f:
            f.write(r.content)
    except Exception as e:
        log(f"Error while downloading plugin: {e}", Status.Danger)
        exit(1)

    add_plugin_zip(os.path.join(get_temp_dir(), "plugin.zip"))
