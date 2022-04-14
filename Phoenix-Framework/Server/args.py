from Utils import *
parser = ArgumentParser("pf")
parser.add_argument("-a", "--address", help="The Ip Address to listen on.",
                    default=socket.gethostbyname(socket.gethostname()), metavar="Address")
parser.add_argument("-p", "--port", help="The Port to listen on.",
                    default=9999, metavar="Port", type=int)
parser.add_argument("-wa", "--waddress", help="The Address of the WebServer",
                    default=socket.gethostbyname(socket.gethostname()))
parser.add_argument(
    "-wp", "--wport", help="The Port of the Web Server", type=int, default=8080)
parser.add_argument("-m", "--mode", help="The Listener Mode.", default="socket",
                    metavar="Mode", choices=["socket", "http"])
