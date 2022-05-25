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
    return render_template("auth/login.html")


@auth.route("/login", methods=["POST"])
def post_login():
    use_json = True if request.args.get("json") == "true" else False
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}) if use_json else render_template("login.html", error="Missing username or password")
    data = check_creds(username, password)
    if data:
        old_user = session.get("username")
        if old_user:
            session["username"] = username
            session["admin"] = True if data[3] else False            
            log(f"{old_user} changed to {username}", "success")
            return jsonify({"status": "success", "message": f"Changed to {username}"}) if use_json else f"Changed to {username}"
        else:
            session["username"] = username
            session["admin"] = True if data[3] else False
            log(f"{'Admin' if data[3] else 'User'} {username} logged in", "success")
            return jsonify({"status": "success", "message": f"Logged in as {username} ({'Admin' if data[3] else 'User'})"}) if use_json else redirect("/")
    else:
        log(f"{username} failed to log in", "warning")
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401 if use_json else redirect("/auth/login")


@auth.route("/logout")
@authorized
def logout():
    use_json = True if request.args.get("json") == "true" else False
    log(f"{'Admin' if session['admin'] else 'User'} {session['username']} logged out", "success")
    session.clear()
    return jsonify({"status": "success", "message": "Logged out"}) if use_json else redirect("/auth/login")

@auth.route("/user", methods=["GET"])
@authorized
def get_user():
    data = {
        "username": session["username"],
        "admin": session["admin"]
    }
    return jsonify(data)

@auth.route("/users/add", methods=["POST"])
@admin
def add_user():
    use_json = True if request.args.get("json") == "true" else False
    username = request.form.get("username")
    password = request.form.get("password")
    admin = True if request.form.get("admin").lower() == "true" else False
    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required"}) if use_json else redirect("/auth/users")

    # Check if user exists
    curr.execute("SELECT * FROM users WHERE username=?", (username,))
    data = curr.fetchone()
    if data:
        return jsonify({"status": "error", "message": "User already exists"}) if use_json else redirect("/auth/add")
    
    # Hash the password
    password = md5(password.encode()).hexdigest()
    curr.execute(f"INSERT INTO users (username, password, admin) VALUES (?, ?, ?)", (username, password, admin))
    conn.commit()
    log(f"({session['username']}) {'Admin' if admin else 'User'} {username} added", "success")
    return jsonify({"status": "success", "message": f"{'Admin' if admin else 'User'} {username} added"}) if use_json else redirect("/auth/add")

@auth.route("/users/remove", methods=["DELETE"])
@admin
def delete_user():
    use_json = True if request.args.get("json") == "true" else False
    username = request.form.get("username")
    if not username:
        return jsonify({"status": "error", "message": "Username required"}) if use_json else abort(400, "Username required")
    
    # Check if user exists
    curr.execute("SELECT * FROM users WHERE username=?", (username,))
    data = curr.fetchone()
    if not data:
        return jsonify({"status": "error", "message": "User does not exist"}) if use_json else abort(404, "User does not exist")
    
    # Check if user is head admin
    if username == "phoenix":
        return jsonify({"status": "error", "message": "Cannot delete the Phoenix Account"}) if use_json else abort(403, "Cannot delete the Phoenix Account")
    # Check if user is the operator
    if username == session["username"]:
        return jsonify({"status": "error", "message": "Cannot delete the your Account"}) if use_json else abort(403, "Cannot delete the your Account")
    # Delete user
    curr.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    log(f"({session['username']}) {'Admin' if data[3] else 'User'} {username} deleted", "success")
    return jsonify({"status": "success", "message": f"Deleted {'Admin' if data[3] else 'User'} {username}"}) if use_json else redirect("/auth/delete")

@auth.route("/users")
@admin
def get_users():
    use_json = True if request.args.get("json") == "true" else False
    curr.execute("SELECT Username, Admin FROM users")
    users = curr.fetchall()
    users = [{"username": user[0], "admin": True if user[1] == 1 else False} for user in users]
    return jsonify({"status": "success", "users": users}) if use_json else render_template("users.html", data=users)

@auth.route("/users/edit", methods=["POST"])
@admin
def edit_user():
    use_json = True if request.args.get("json") == "true" else False
    username = request.form.get("username")
    change = request.form.get("change")
    value = request.form.get("value")
    if not username or not change or not value:
        return jsonify({"status": "error", "message": "Username, change and value required"}) if use_json else abort(400, "Username, change and value required")
    # Check if user exists
    curr.execute("SELECT * FROM users WHERE username=?", (username,))
    data = curr.fetchone()
    if not data:
        return jsonify({"status": "error", "message": "User does not exist"}) if use_json else abort(404, "User does not exist")
    # Check if user is head admin
    if username == "phoenix" and session["username"] != "phoenix":
        return jsonify({"status": "error", "message": "Cannot edit the Phoenix Account"}) if use_json else abort(403, "Cannot edit the Phoenix Account")
    # Edit user
    if change == "admin":
        value = 1 if value.lower() == "true" else 0
        curr.execute("UPDATE users SET admin=? WHERE username=?", (value, username))
        conn.commit()
        log(f"({session['username']}) Updated {username}'s permissions to {'Admin' if value == 1 else 'User'}", "success")
        return jsonify({"status": "success", "message": f"{'Admin' if value else 'User'} {username} edited"}) if use_json else redirect("/auth/edit")
    elif change == "password":
        value = md5(value.encode()).hexdigest()
        curr.execute("UPDATE users SET password=? WHERE username=?", (value, username))
        conn.commit()
        log(f"({session['username']}) Updated {username}'s password", "success")
        return jsonify({"status": "success", "message": f"{username}'s password edited"}) if use_json else redirect("/auth/edit")
    elif change == "username":
        curr.execute("UPDATE users SET username=? WHERE username=?", (value, username))
        conn.commit()
        log(f"({session['username']}) Updated {username}'s username to {value}", "success")
        return jsonify({"status": "success", "message": f"{username}'s username edited"}) if use_json else redirect("/auth/edit")
    else:
        return jsonify({"status": "error", "message": "Invalid change"}) if use_json else abort(400, "Invalid change")
    
