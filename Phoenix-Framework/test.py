import threading

from flask import Flask
from werkzeug.serving import make_server


class ServerThread(threading.Thread):

    def __init__(self, app: Flask):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


app = Flask('myapp')
server = ServerThread(app)
server.start()
input(">")
server.shutdown()
input(">")
server.start()