from Utils import *
from functools import wraps
auth = Blueprint("auth", __name__, url_prefix="/auth")


def authorized(func):
    """Check if a user is logged in and redirect to login page if not"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
        # for testing
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
        log(f"{username} logged in", "success")
        return redirect(url_for("routes.index"))
    else:
        log(f"{username} failed to log in", "error")
        return render_template("login.html", error="Invalid Credentials")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.index"))

@auth.route("/user", methods=["GET"])
@authorized
def get_user():
    data = {
        "username": session["username"],
        "admin": session["admin"]
    }
    return jsonify(data)

@auth.route("/add", methods=["POST"])
@admin
def add_user():
    username = request.form.get("username")
    password = request.form.get("password")
    admin = True if request.form.get("admin").lower() == "true" else False
    if not username or not password:
        abort(400)

    # Check if user exists
    curr.execute("SELECT * FROM users WHERE username=?", (username,))
    data = curr.fetchone()
    if data:
        abort(409)
    
    # Hash the password
    password = md5(password.encode()).hexdigest()
    curr.execute(f"INSERT INTO users (username, password, admin) VALUES (?, ?, ?)", (username, password, admin))
    conn.commit()
    log(f"{'Admin' if admin else 'User'} {username} added", "success")
    return f"{'Admin' if admin else 'User'} {username} added"

