try:
    from globals import *
    from Handlers.SOCKET import SOCKET
    from Handlers.HTTP import HTTP
    from Web import create_web
except ImportError:
    print("[ERROR] Not all required Libraries are installed.")
    exit()


# Database
conn = connect("Data/db.sqlite3")
curr = conn.cursor()
try:
    curr.execute("SELECT * FROM Devices")
    curr.fetchall()
except:
    print("[ERROR] Database isnt configured.")
    exit()
# Argparser
parser = ArgumentParser("Phoenix-Framework")
parser.add_argument("-a", "--address", help="The Ip Address to listen on.",
                    default=socket.gethostbyname(socket.gethostname()), metavar="Address")
parser.add_argument("-p", "--port", help="The Port to listen on.",
                    default=9999, metavar="Port", type=int)
parser.add_argument("-aa", "--aaddress", help="The Address of the WebServer",
                    default=socket.gethostbyname(socket.gethostname()))
parser.add_argument(
    "-ap", "--aport", help="The Port of the Web Server", type=int, default=8080)
parser.add_argument("-m", "--mode", help="The Listener Mode.", default="socket",
                    metavar="Mode", choices=["socket", "http"])

if __name__ == "__main__":
    ph_print(logo)
    args = parser.parse_args()
    # Get Arguments
    api_address = args.aaddress
    api_port = args.aport
    mode = args.mode
    port = args.port
    address = args.address
    # Start Handler
    log(f"Starting {mode.upper()} Handler.", alert="info")
    try:
        if mode == "socket":
            Handler = SOCKET(address, port)
        else:
            Handler = HTTP(address, port)
    except:
        log("Could not start Handler,\nplease look at the logs for more information.", "error")
        exit()
    else:
        log(f"Handler started.", alert="success")
        log(f"Listening on {address}:{port}", alert="info")
    # Create Web Server
    Api = create_web(Handler)
    # Start Web Server
    log("Starting Web Server", "info")
    try:
        threading.Thread(target=Api.run, kwargs={
                               "host": api_address, "port": api_port}, name="WebServer").start()
    except:
        log("Could not start Api Server", "error")
        exit()
    else:
        log("Api Server started", "success")
    log(f"Accessible at http://{api_address}:{api_port}", "info")
    log(f"Press CTRL+C to exit.", "info")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            Handler.stop()
            log("Exiting", alert="info")
            exit()
        except:
            log("Unknown Error", alert="critical")
            exit()
