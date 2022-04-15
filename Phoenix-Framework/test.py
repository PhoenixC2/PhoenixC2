from Utils import *
from Server import * 
listeners = [(1, "ReverseSocketTcpListener1", "socket/reverse/tcp", '{"address": "0.0.0.0", "port": 8090}')]
print(listeners)

server = Server_Class()
# Start Listeners
for listener in listeners:
    type = listener[2]
    type = type.replace("/", ".")
    type = "Listeners." + type
    config = json.loads(listener[3])
    # Get the Listener from the File
    listener = importlib.import_module(type).Listener(
        server, config, len(server.listeners) + 1)
    listener.start()
    server.add_listener(listener)

