import datetime
import threading
from functools import wraps

from Database import LogEntryModel, Session, UserModel
from flask import (Flask, Response, abort, flash, jsonify, redirect, request,
                   session)
from werkzeug.serving import make_server


def get_messages() -> list[LogEntryModel]:
    return [log for log in Session.query(LogEntryModel).all() if get_current_user() in log.unseen_users]
def generate_response(alert: str, text: str, redirect_location: str = "", response_code: int = 200) -> Response:
    """Generate the Endpoint Response"""
    use_json = request.args.get("json", "").lower() == "true"
    if use_json:
        return jsonify({"status": alert, "message": text}), response_code
    flash(text, alert)
    return redirect("/" + redirect_location)


def get_current_user() -> UserModel | None:
    """Get the user object or None"""
    if request.headers.get("Api-Key") is not None:
        user = Session.query(UserModel).filter_by(
            api_key=request.headers.get("Api-Key")).first()
        if user is not None:
            return user
    return Session.query(UserModel).filter_by(password=session.get("password")).first()


def authorized(func):
    """Check if a user is logged in and redirect to login page if not"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if user is None:
            abort(401)
        else:
            if user.disabled:
                flash("Your account got disabled!", "error")
                session.clear()
                return redirect("/auth/login")
            user.last_activity = datetime.datetime.now()
            Session.commit()
            return func(*args, **kwargs)
    return wrapper


def admin(func):
    """Check if a user is admin and redirect to login page if not"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if user is not None:
            if not user.admin:
                abort(403)
            else:
                return func(*args, **kwargs)
        else:
            abort(401)
    return wrapper

class FlaskThread(threading.Thread):
    """Stoppable Flask server"""
    def __init__(self, app: Flask, address: str, port: int, ssl: bool, name:str):
        @app.teardown_request
        def remove(*args, **kwargs):
            Session.remove()
        threading.Thread.__init__(self)
        self.name = name
        if ssl:
            self.server = make_server(address, port, app, threaded=True, ssl_context=("Data/ssl.pem", "Data/ssl.key"))
        else:
            self.server = make_server(address, port, app, threaded=True)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()