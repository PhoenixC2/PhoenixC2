#!/usr/bin/env python3

import os
import time

from phoenix_framework.server.args import parse_args, parser
from phoenix_framework.server.commander import Commander
from phoenix_framework.server.commander.services import (load_plugins,
                                                         start_listeners,
                                                         start_web)
from phoenix_framework.server.utils.admin import check_for_setup, reset_server
from phoenix_framework.server.utils.config import load_config
from phoenix_framework.server.utils.ui import log


def main():
    args = parser.parse_args()
    os.environ["PHOENIX_CONFIG_PATH"] = args.config  # set config path

    config = load_config()
    config = parse_args(args, config)

    log("Welcome to Phoenix Framework.", "success")

    if not check_for_setup():
        reset_server()

    # Initialize commander
    commander = Commander()

    # Start listeners
    log("Starting listeners.", "info")
    start_listeners(commander)

    # Start the web server
    log("Starting web server.", "info")
    try:
        web_config = config["web"]  # shorten code
        start_web(
            web_config["address"], web_config["port"], web_config["ssl"], commander
        )
    except Exception as e:
        log(str(e), "danger")
        os._exit(1)
    else:
        log("Web server started.", "success")

    log(
        f"Accessible at http{'s' if web_config['ssl'] else ''}"
        f"://{web_config['address']}:{web_config['port']}",
        "info",
    )

    # load plugins
    log("Loading plugins.", "info")
    load_plugins(commander)

    log(f"Press CTRL+C to exit.", "info")
    if args.quiet:
        print("Finished startup.")
    while True:
        try:
            # print(input("Server > "))
            time.sleep(1)
        except KeyboardInterrupt:
            log("Exiting", alert="info")
            os._exit(0)


if __name__ == "__main__":
    main()
