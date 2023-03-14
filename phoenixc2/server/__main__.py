#!/usr/bin/env python3

import os
import time

from phoenixc2.server.args import parse_args, parser
from phoenixc2.server.web import create_web
from phoenixc2.server.commander import Commander
from phoenixc2.server.commander.services import load_plugins, start_listeners, start_web
from phoenixc2.server.utils.admin import check_for_setup, reset_server
from phoenixc2.server.utils.config import load_config
from phoenixc2.server.utils.ui import log
from phoenixc2.server.utils.misc import Status


def main():
    args = parser.parse_args()
    os.environ["PHOENIX_CONFIG_PATH"] = args.config  # set config path

    config = load_config()
    config = parse_args(args, config)

    log("Welcome to PhoenixC2", Status.Success)

    if not check_for_setup():
        reset_server()

    # Initialize commander
    commander = Commander()

    # Create web server
    web_server = create_web(commander)

    commander.web_server = web_server

    # load plugins
    log("Loading plugins.", Status.Info)
    load_plugins(commander)

    # Start listeners
    log("Starting listeners.", Status.Info)
    start_listeners(commander)

    # Start the web server
    log("Starting web server.", Status.Info)
    try:
        web_config = config["web"]  # shorten code
        start_web(
            web_config["address"], web_config["port"], web_config["ssl"], commander
        )
    except Exception as e:
        log(str(e), Status.Danger)
        os._exit(1)
    else:
        log("Web server started.", Status.Success)

    log(
        f"Accessible at http{'s' if web_config['ssl'] else ''}"
        f"://{web_config['address']}:{web_config['port']}",
        Status.Info,
    )

    log("Press CTRL+C to exit.", Status.Info)
    if args.quiet:
        print("Finished startup.")
    if args.exit:
        os._exit(0)
    while True:
        try:
            # print(input("Server > "))
            time.sleep(1)
        except KeyboardInterrupt:
            log("Exiting", status=Status.Info)
            os._exit(0)


if __name__ == "__main__":
    main()
