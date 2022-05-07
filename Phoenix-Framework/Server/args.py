"""Argument Parsing for the Server."""
from Utils import *
parser = ArgumentParser("pfserver", usage="sudo pfserver [options]", description="Start the Phoenix Framework Server.")
parser.add_argument("-a", "--address", help="The Address of the WebServer",
                    default=socket.gethostbyname(socket.gethostname()))
parser.add_argument(
    "-p", "--port", help="The Port of the Web Server", type=int, default=8080)
parser.add_argument("-s", "--ssl", help="Use SSL", action="store_true")