import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm import scoped_session, sessionmaker

from phoenixc2.server.utils.config import load_config
from phoenixc2.server.utils.ui import log
from phoenixc2.server.utils.resources import get_resource

c = load_config()["database"]

if c["type"] == "sqlite":
    if c["sqlite_name"] == "memory":
        conn_string = "sqlite:///:memory:"
    else:
        conn_string = (
            "sqlite:///"
            + str(get_resource("data", c["sqlite_name"], skip_file_check=True))
            + ".sqlite3"
        )

else:
    conn_string = (
        f"{c['type']}://{c['user']}:{c['pass']}@{c['host']}:{c['port']}/{c['database']}"
    )

# check if database verbose is enabled
echo = "3" in os.getenv("PHOENIX_DEBUG", "") or "4" in os.getenv("PHOENIX_DEBUG", "")
engine = create_engine(conn_string, echo=echo)

try:
    engine.connect()
except Exception as e:
    log(f"Failed to connect to database: {e}", "critical")
    choice = input("Do you want to switch to sqlite? [y/N]: ") or "y"
    if choice.lower() == "y":
        log("Switching to sqlite...", "warning")
        conn_string = (
            "sqlite:///"
            + str(get_resource("data", c["sqlite_name"], skip_file_check=True))
            + ".sqlite3"
        )
        engine = create_engine(conn_string, echo=echo)
    else:
        exit(1)


Session: SessionType = scoped_session(sessionmaker(bind=engine))
