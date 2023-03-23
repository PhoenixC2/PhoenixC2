import sys
import os

if __name__ == "__main__":
    if sys.argv[1] == "server":
        from .server.__main__ import main

    elif sys.argv[1] == "client":
        from .client.__main__ import main

    elif sys.argv[1] == "test":
        test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")
        sys.exit(os.system(f"python -m unittest {test_path}/*.py"))

    else:
        print("Usage: python -m phoenixc2 [server|client|test]")
        sys.exit(1)

    sys.argv.pop(1)
    sys.exit(main())
