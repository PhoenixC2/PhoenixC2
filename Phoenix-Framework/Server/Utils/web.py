import datetime
from functools import wraps

from Database import UserModel, db_session
from flask import Response, abort, flash, jsonify, redirect, request, session


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
        user = db_session.query(UserModel).filter_by(
            api_key=request.headers.get("Api-Key")).first()
        if user is not None:
            return user
    return db_session.query(UserModel).filter_by(id=session.get("id")).first()


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
            db_session.commit()
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
