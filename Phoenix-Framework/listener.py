import time
import threading
from multiprocessing import Process
from flask import Flask, request


class Listener(Flask):
    """The Reverse Http Listener Class"""
    api = Flask()
    def __init__(self):
        super().__init__()
        self.address = "0.0.0.0"
        self.port = 9999
        self.handlers: list = []
        self.listener_thread: threading.Thread
        self.refresher_thread: threading.Thread

    @api.route("/connect")
    def _connect(self):
        request.re

    def listen()