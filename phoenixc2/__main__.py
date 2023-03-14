import sys

if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] not in ["server", "client"]:
        print("Usage: python -m phoenixc2 [server|client]")
        sys.exit(1)

    if sys.argv[1] == "server":
        from .server.__main__ import main

        sys.argv.pop(1)
        sys.exit(main())
    elif sys.argv[1] == "client":
        from .client.__main__ import main

        sys.argv.pop(1)
        sys.exit(main())
