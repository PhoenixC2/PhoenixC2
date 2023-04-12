#!/usr/bin/env python3

import os
import time

from phoenixc2.server.args import parse_args, parser
from phoenixc2.server.commander.commander import Commander
from phoenixc2.server.commander.services import load_plugins, start_listeners, start_api
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

    # Create the API
    api = create_api(commander)

    commander.api = api

    # load plugins
    log("Loading plugins.", Status.Info)
    load_plugins(commander)

    # Start listeners
    log("Starting listeners.", Status.Info)
    start_listeners(commander)

    # Start the API
    log("Starting Rest API.", Status.Info)
    try:
        api_config = config["api"]  # shorten code
        start_api(
            api_config["address"], api_config["port"], api_config["ssl"], commander
        )
    except Exception as e:
        log(str(e), Status.Danger)
        os._exit(1)
    else:
        log("Rest API started.", Status.Success)

    log(
        f"Accessible at http{'s' if api_config['ssl'] else ''}"
        f"://{api_config['address']}:{api_config['port']}",
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
