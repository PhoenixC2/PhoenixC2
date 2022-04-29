from Utils import *
from functools import wraps
auth = Blueprint("auth", __name__, url_prefix="/auth")


def authorized(func):
    """Check if a user is logged in and redirect to login page if not"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("username"):
            abort(401)
        else:
            return func(*args, **kwargs)
    return wrapper


def admin(func):
    """Check if a user is admin and redirect to login page if not"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            abort(403)
        return func(*args, **kwargs)
    return wrapper

def check_creds(username, password):
    # hash the password
    password = md5(password.encode()).hexdigest()
    try:
        curr.execute(
            "SELECT * FROM users WHERE username=? AND password=?", (username, password))
        data = curr.fetchone()
        if data:
            return data
        else:
            return False
    except OperationalError:
        return False


@auth.route("/login", methods=["GET"])
def get_login():
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def post_login():
    username = request.form.get("username")
    password = request.form.get("password")
    data = check_creds(username, password)
    if data:
        session["username"] = username
        session["admin"] = False
        return redirect(url_for("routes.index"))
    else:
        return render_template("login.html", error="Invalid Credentials")
