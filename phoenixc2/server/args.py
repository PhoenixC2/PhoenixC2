"""Arguments for the server."""
import logging
import os
from argparse import ArgumentParser

import phoenixc2
from phoenixc2.server.database.base import Base
from phoenixc2.server.utils.admin import (
    recreate_super_user,
    regenerate_ssl,
    generate_database,
    setup_server,
    reset_table,
)
from phoenixc2.server.utils.ui import log, logo, ph_print

parser = ArgumentParser(
    "phserver",
    usage="phserver [options]",
    description="Start the PhoenixC2 server.",
)

api = parser.add_argument_group("Rest API")
api.add_argument("-a", "--address", help="The address")
api.add_argument("-p", "--port", help="The port", type=int)
api.add_argument("-s", "--ssl", help="Use SSL", action="store_true")

output = parser.add_argument_group("Output")

output.add_argument(
    "-d",
    "--debug",
    help="Enable debug output for services: Actions: 1 Flask: 2 Database: 3 All: 4",
    action="append",
)
output.add_argument("-b", "--banner", help="Disable banner", action="store_true")
output.add_argument("-q", "--quiet", help="Disable all output", action="store_true")

misc = parser.add_argument_group("Misc")
misc.add_argument(
    "-t",
    "--test",
    help="Start a test version with disabled authentication",
    action="store_true",
)
misc.add_argument(
    "-v", "--version", help="Print the version and exit", action="store_true"
)
misc.add_argument(
    "-c",
    "--config",
    help="Name of the config file to use. [default.toml]",
    default="default.toml",
)
misc.add_argument(
    "-e",
    "--exit",
    help="Exit after the server has been started(used for testing)",
    action="store_true",
)
admin = parser.add_argument_group("Admin")
admin.add_argument(
    "-r",
    "--reset",
    help="Reset the server to the default state",
    action="store_true",
)
admin.add_argument(
    "--recreate-super-user", help="Recreate the super user.", action="store_true"
)
admin.add_argument("--backup-database", help="Backup database to the given location.")
admin.add_argument("--reset-database", help="Reset the database", action="store_true")
admin.add_argument(
    "--reset-table",
    help="Reset a specified database table.",
    choices=[table.lower() for table in Base.metadata.tables.keys()],
)

admin.add_argument(
    "--regenerate-ssl",
    help="Regenerate the ssl certificates",
    action="store_true",
)


def parse_args(args, config: dict) -> dict:
    # output args
    if args.version:
        ph_print("PhoenixC2 Server v" + phoenixc2.__version__)
        exit()
    if args.quiet and args.debug:
        log("-q and -d are mutually exclusive.", "error")
        exit()
    if args.quiet:
        os.environ["PHOENIX_PRINT"] = "false"
        log("Starting PhoenixC2 in quiet mode.", "info")
    if args.debug:
        os.environ["PHOENIX_DEBUG"] = str(args.debug)
        logging.basicConfig(
            level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    ph_print(logo, args.banner)

    if args.test:
        os.environ["PHOENIX_TEST"] = "true"
        log(
            "Starting PhoenixC2 in test mode. AUTHENTICATION DISABLED!",
            "critical",
        )

    # admin args
    if args.reset:
        if (
            input("Are you sure, that you want to reset the server [Y/n]: ").lower()
            == "y"
        ):
            setup_server(reset=True)
        else:
            log("Database reset aborted.", "info")
    if args.recreate_super_user:
        recreate_super_user()
    if args.reset_database:
        if (
            input("Are you sure, that you want to reset the database [Y/n]: ").lower()
            == "y"
        ):
            generate_database(True)
        else:
            log("Database reset aborted.", "info")
    if (
        args.reset_table
        and input(
            f"Are you sure, that you want to reset the table {args.reset_table} [Y/n]: "
        ).lower()
        == "y"
    ):
        reset_table(args.reset_table)
    if args.regenerate_ssl:
        regenerate_ssl()

    # api args
    if args.address:
        config["api"]["address"] = args.address
    if args.port:
        config["api"]["port"] = args.port
    if args.ssl:
        config["api"]["ssl"] = args.ssl

    return config
