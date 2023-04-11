#!/usr/bin/env python3

import os
import time

from phoenixc2.server.args import parse_args, parser
from phoenixc2.server.commander.commander import Commander
from phoenixc2.server.commander.services import load_plugins, start_listeners, start_web
from phoenixc2.server.utils.admin import check_for_setup, setup_server
from phoenixc2.server.utils.config import load_config
from phoenixc2.server.utils.misc import Status
from phoenixc2.server.utils.ui import log
from phoenixc2.server.api import create_api
from phoenixc2.utils.update import check_for_update


def main():
    args = parser.parse_args()
    os.environ["PHOENIX_CONFIG_PATH"] = args.config  # set config path

    config = load_config()
    config = parse_args(args, config)

    log("Welcome to PhoenixC2", Status.Success)
    check_for_update()
    if not check_for_setup():
        setup_server()
    if args.exit:
        os._exit(0)
    # Initialize commander
    commander = Commander()

    # Create web server
    api = create_api(commander)

    commander.api = api

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
    while True:
        try:
            # print(input("Server > "))
            time.sleep(1)
        except KeyboardInterrupt:
            log("Exiting", status=Status.Info)
            os._exit(0)


if __name__ == "__main__":
    main()
