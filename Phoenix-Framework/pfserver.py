# Change Directory
#import os
# os.chdir("/usr/share/phoenix-framework")
try:
    from Utils import *
    import Server as srv
except ImportError:
    print("[ERROR] Not all required Libraries are installed.")
    exit()

if __name__ == "__main__":
    ph_print(logo)

    # Check if the user is root
    if not os.getuid() == 0:
        log("Please start with Sudo or Root Rights", "error")
        exit()

    # Check Database
    try:
        check_db()
    except Exception as e:
        print("[ERROR] " + str(e))
        exit()

    # Get Arguments
    args = srv.parser.parse_args()

    # Initialize Server
    server = srv.Server_Class()

    # Start Listeners
    try:
        srv.start_listeners(server, curr)
    except Exception as e:
        print("[ERROR] " + str(e))
        exit()
    
    # Start the web srv
    log("Starting Web srv", "info")
    try:
        web = srv.start_web(args.waddress, args.wport)
        pass
    except Exception as e:
        log(str(e), "error")
        exit()
    else:
        log("Web Server started", "success")

    log(f"Accessible at http://{args.waddress}:{args.wport}", "info")
    log(f"Press CTRL+C to exit.", "info")

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            log("Exiting", alert="info")
            exit()
        except:
            log("Unknown Error", alert="critical")
            exit()
