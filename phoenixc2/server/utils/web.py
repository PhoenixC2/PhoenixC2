import threading
import os
import bleach
import markdown
from flask import Flask
from werkzeug.serving import make_server
from werkzeug.debug import DebuggedApplication
from phoenixc2.server.database import Session
from phoenixc2.server.utils.resources import get_resource


def clean_markdown(content: str) -> str:
    """Clean the markdown content"""
    return bleach.clean(
        content,
        tags=["p", "strong", "em", "a"],
        attributes={
            "a": ["href", "title"],
            "img": ["src", "alt"],
        },
    )


def generate_html_from_markdown(content: str) -> str:
    """Generate HTML from Markdown"""
    return markdown.markdown(content, extensions=["markdown.extensions.fenced_code"])


class FlaskThread(threading.Thread):
    """Stoppable Flask thread"""

    def __init__(self, app: Flask, address: str, port: int, ssl: bool, name: str):
        threading.Thread.__init__(self)

        @app.teardown_request
        def remove(*args, **kwargs):
            Session.remove()

        self.app = app
        self.name = name

        # enable debug mode and reloader if PHOENIX_DEBUG is set to 1
        if "2" in os.environ.get("PHOENIX_DEBUG", "0") or "4" in os.environ.get(
            "PHOENIX_DEBUG", "0"
        ):
            self.app = DebuggedApplication(self.app, evalex=True)

        if ssl:
            self.server = make_server(
                address,
                port,
                self.app,
                threaded=True,
                ssl_context=(
                    str(get_resource("data", "ssl.pem")),
                    str(get_resource("data", "ssl.key")),
                ),
            )
        else:
            self.server = make_server(address, port, self.app, threaded=True)

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()
