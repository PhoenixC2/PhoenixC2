"""Arguments for the server."""
import os
import logging
from argparse import ArgumentParser
from phoenix_framework.server.utils.ui import ph_print, logo, log
from phoenix_framework.server.utils.admin import recreate_ssl, recreate_super_user, reset_database
from phoenix_framework.server import version

parser = ArgumentParser(
    "pfserver",
    usage="pfserver [options]",
    description="Start the Phoenix-Framework C2 server.",
)

web = parser.add_argument_group("Web Server")
web.add_argument("-a", "--address", help=f"The address")
web.add_argument("-p", "--port", help="The port", type=int)
web.add_argument("-s", "--ssl", help="Use SSL", action="store_true")

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
    help="Start a test version with disabled authorization",
    action="store_true",
)
misc.add_argument(
    "-v", "--version", help="Print the version and exit", action="store_true"
)
misc.add_argument(
    "-l",
    "--location",
    help="The location of the framework [/usr/share/Phoenix-Framework]",
    default="/usr/share/Phoenix-Framework/Server",
)
misc.add_argument(
    "-c",
    "--config",
    help="Location of the config file. [/usr/share/Phoenix-Framework/Server/Data/config.toml]",
    default="/usr/share/Phoenix-Framework/Server/Data/config.toml",
)
admin = parser.add_argument_group("Admin")
admin.add_argument(
    "--recreate-super-user", help="Recreate the super user.", action="store_true"
)
admin.add_argument("--backup-database", help="Backup database to the given location.")
admin.add_argument("--reset-database", help="Reset the database", action="store_true")
admin.add_argument(
    "--reset-database-table",
    help="Reset a specified database table.",
    choices=[
        "users",
        "listeners",
        "stagers",
        "credentials",
        "operations",
        "devices",
        "logs",
    ],
)

admin.add_argument("--degrade", help="Degrade to a sub server", action="store_true")
admin.add_argument(
    "--promote", help="Promote the to a main server", action="store_true"
)
admin.add_argument(
    "--recreate-ssl-certificates",
    help="Recreate the ssl certificates",
    action="store_true",
)


def parse_args(args, config : dict) -> dict:

    # output args
    if args.version:
        ph_print("Phoenix Framework C2 Server v" + version)
        exit()
    if args.quiet and args.debug:
        log("-q and -d are mutually exclusive.", "error")
        exit()
    if args.quiet:
        os.environ["PHOENIX_LOG"] = "false"
        log("Starting Phoenix-Framework in quiet mode.", "info")
    if args.debug:
        os.environ["PHOENIX_DEBUG"] = str(args.debug)
        logging.basicConfig(
            level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    ph_print(logo, args.banner)

    if args.test:
        os.environ["PHOENIX_TEST"] = "true"
        log(
            "Starting Phoenix Framework in test mode. AUTHORIZATION DISABLED!",
            "critical",
        )


    # admin args
    if args.reset_database:
        if input("Are you sure, that you want to reset the database [Y/n]: ").lower() == "y":
            reset_database()
    if args.recreate_super_user:
        recreate_super_user()
    if args.recreate_ssl_certificates:
        recreate_ssl()
    
    # web-server args
    # replace config data with args if they are specified

    if args.address:
        config["web"]["address"] = args.address
    if args.port:
        config["web"]["port"] = args.port
    if args.ssl:
        config["web"]["ssl"] = args.ssl
    
    return config