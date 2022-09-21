from multiprocessing import Process
from threading import Thread

from flask import Flask, request


class Listener():
    """The Reverse Http Listener Class"""
    api = Flask(__name__)

    def __init__(self):
        super().__init__()
        self.address = "0.0.0.0"
        self.port = 9999
        self.handlers: list = []
        self.listener_process: Process
        self.create_api()

    def create_api(self):
        self.api = Flask(__name__)

        @self.api.route("/connect", methods=["POST"])
        def connect():
            data = request.get_json()

    def start(self):
        self.listener_process = Process(target=self.api.run)
        Thread(target=self.listener_process.start).start()

    def stop(self):
        self.listener_process.kill()


listener = Listener()
listener.start()
input()
listener.stop()
