import threading

import bleach
import markdown
from flask import Flask
from werkzeug.serving import make_server

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
        from phoenixc2.server.database import Session

        threading.Thread.__init__(self)

        @app.teardown_request
        def remove(*args, **kwargs):
            Session.remove()

        self.app = app
        self.name = name
        if ssl:
            self.server = make_server(
                address,
                port,
                app,
                threaded=True,
                ssl_context=(
                    str(get_resource("data", "ssl.pem")),
                    str(get_resource("data", "ssl.key")),
                ),
            )
        else:
            self.server = make_server(address, port, app, threaded=True)

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()
