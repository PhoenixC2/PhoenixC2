from Utils.libraries import (
    Blueprint,
    abort,
    session,
    request,
    render_template,
    jsonify,
    redirect,
    flash,
    escape)
from Utils.ui import log
from Database import session as db_session, UserModel
from functools import wraps

auth = Blueprint("auth", __name__)


def get_current_user(user_id: int) -> UserModel:
    """Get the user object using the user id"""
    return db_session.query(UserModel).filter_by(user_id=user_id).first()


def authorized(func):
    """Check if a user is logged in and redirect to login page if not"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("id"):
            abort(401)
        else:
            return func(*args, **kwargs)
    return wrapper


def admin(func):
    """Check if a user is admin and redirect to login page if not"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("id"):
            if not get_current_user(session.get("id")).admin:
                abort(403)
            else:
                return func(*args, **kwargs)
        else:
            abort(401)
    return wrapper


@auth.route("/login", methods=["GET"])
def get_login():
    return render_template("auth/login.html")


@auth.route("/login", methods=["POST"])
def post_login():
    use_json = request.args.get("json") == "true"
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        if not use_json:
            flash("Missing username or password.", "error")
            render_template("login.html")
        return jsonify({"status": "error", "message": "Missing username or passwor.d"})

    user: UserModel = db_session.query(
        UserModel).filter_by(username=username).first()

    if user.disabled:
        log(f"{username} failed to log in because the account is disabled.", "warning")

        if not use_json:
            flash("Account is disabled.", "error")
            redirect("/auth/login")
        return jsonify({"status": "error", "message": "Account is disabled."}), 401

    if user.check_password(password):
        old_user = session.get("username")

        if old_user and old_user != username:
            session["id"] = user.user_id
            log(f"{old_user} changed to {username}.", "success")

            if not use_json:
                flash(f"Changed to {username}.", "success")
                redirect("/")
            return jsonify({"status": "success", "message": f"Changed to {username}."})
        else:
            session["id"] = user.user_id
            log(f"{'Admin' if user.admin else 'User'} {username} logged in.", "success")
            if not use_json:
                flash(
                    f"Logged in as {username} ({'Admin' if user.admin else 'User'}).", "success")
                redirect("/")
            return jsonify({"status": "success", "message": f"Logged in as {username} ({'Admin' if user.admin else 'User'})."})
    else:
        log(f"{username} failed to log in", "warning")

        if not use_json:
            flash("Invalid username or password.", "error")
            return render_template("login.html", username=username)
        return jsonify({"status": "error", "message": "Invalid username or password."}), 401


@auth.route("/logout")
@authorized
def logout():
    use_json = request.args.get("json") == "true"
    user = get_current_user(session["id"])
    log(f"{'Admin' if user.admin else 'User'} {user.username} logged out.", "success")
    session.clear()
    if not use_json:
        flash("Logged out", "success")
        redirect("/login")
    return jsonify({"status": "success", "message": "Logged out."})


@auth.route("/users", methods=["GET"])
@authorized
def get_users():
    use_json = request.args.get("json") == "true"
    user = get_current_user(session["id"])
    users = db_session.query(UserModel).all()
    return jsonify({"status": "success", "users": users}) if use_json else render_template("users.html", user=user, users=users)


@auth.route("/users/add", methods=["POST"])
@admin
def add_user():
    use_json = request.args.get("json") == "true"
    username = request.form.get("username")
    password = request.form.get("password")
    admin = request.form.get("admin").lower() == "true"
    disabled = request.form.get("disabled").lower() == "true"

    if not username or not password:
        if not use_json:
            flash("Username and password required.")
            redirect("/users")
        return jsonify({"status": "error", "message": "Username and password required."})

    # Check if user exists
    if db_session.query(UserModel).filter_by(username=username).first():
        if not use_json:
            flash("User already exists.", "error")
            return redirect("/users")
        return jsonify({"status": "error", "message": "User already exists."})

    user = UserModel(
        username=username,
        admin=admin,
        disabled=disabled)
    user.set_password(password)

    db_session.add(user)
    db_session.commit()
    log(f"({get_current_user(session.get('id')).username}) added {'Admin' if admin else 'User'} {username}.", "success")
    if not use_json:
        flash(f"{'Admin' if admin else 'User'} {username} added.", "success")
        return redirect("/users")
    return jsonify({"status": "success", "message": f"{'Admin' if admin else 'User'} {username} added."})


@auth.route("/users/remove", methods=["DELETE"])
@admin
def delete_user():
    use_json = request.args.get("json") == "true"
    username = request.form.get("username")
    current_user = get_current_user(session.get("id"))
    if not username:
        if not use_json:
            flash("Username required.")
            abort
        return jsonify({"status": "error", "message": "Username required."})
    # Check if user exists
    user: UserModel = db_session.query(UserModel).first()
    if not user:
        if not use_json:
            flash("User does not exist.", "error")
            return redirect("/users")
        return jsonify({"status": "error", "message": "User does not exist."})

    # Check if user is head admin
    if username == "phoenix":
        if not use_json:
            flash("Can't delete the Phoenix Account.")
            return redirect("/users")
        return jsonify({"status": "error", "message": "Can't delete the Phoenix Account."})
    # Check if user is the operator
    if username == current_user.username:
        if not use_json:
            flash("Cannot delete your own Account")
            return redirect("/users")
        return jsonify({"status": "error", "message": "Can't delete your own Account."})
    # Delete user
    db_session.delete(user)
    log(f"({session['username']}) deleted {'Admin' if user.admin else 'User'} {username}.", "success")
    if not use_json:
        flash(
            f"Deleted {'Admin' if user.admin else 'User'} {username}", "success")
        return redirect("/users")
    return jsonify({"status": "success", "message": f"Deleted {'Admin' if user.admin else 'User'} {username}."})


@auth.route("/users/edit", methods=["POST"])
@admin
def edit_user():
    use_json = request.args.get("json") == "true"
    username = request.form.get("username", "")
    change = request.form.get("change", "")
    value = request.form.get("value", "")
    if not all([username, change, value]):
        if not use_json:
            flash("Username, change and value required.", "error")
            return redirect("/users")
        return jsonify({"status": "error", "message": "Username, change and value required."})
    # Check if user exists
    current_user = get_current_user(session.get("id"))
    user: UserModel = db_session.query(
        UserModel).filter_by(username=username).first()
    if not user:
        if not use_json:
            flash("User doesn't exist.", "error")
            return redirect("/users")
        return jsonify({"status": "error", "message": "User does not exist."})

    # Check if user is head admin
    if username == "phoenix" and current_user.username != "phoenix":
        if not use_json:
            flash("Cannot edit the Phoenix Account.", "error")
            return redirect("/users")
        return jsonify({"status": "error", "message": "Cannot edit the Phoenix Account."})
    # Edit user
    if change == "admin":
        user.admin = value.lower() == "true"
        db_session.commit()
        log(f"({session['username']}) updated {username}'s permissions to {'Admin' if user.admin else 'User'}.", "success")
        if not use_json:
            flash(
                f"Updated {username}'s permissions to {'Admin' if user.admin else 'User'}.", "success")
            return redirect("/users")
        return jsonify({"status": "success", "message": f"Updated {username}'s permissions to {'Admin' if user.admin else 'User'}."})
    elif change == "password":
        user.set_password(value)
        db_session.commit()
        log(f"({session['username']}) Updated {username}'s password.", "success")
        if not use_json:
            flash(f"{username}'s password edited.", "success")
            return redirect("/users")
        return jsonify({"status": "success", "message": f"{username}'s password edited."})
    elif change == "username":
        if db_session.query(UserModel).filter_by(username=value).first() or value == "":
            if not use_json:
                flash("Name is already in use.", "error")
                return redirect("/users")
            return jsonify({"status": "errror", "message": "Name is already in use."})
        user.username = str(escape(value))
        db_session.commit()
        log(f"({session['username']}) updated {username}'s username to {value}.", "success")
        if not use_json:
            flash(f"Updated {username}'s username to {value}.", "success")
            return redirect("/users")
        return jsonify({"status": "success", "message": f"{username}'s username edited."})
    elif change == "disabled":
        user.disabled = value.lower() == "true"
        db_session.commit()
        log(f"{current_user.username} disabled {'Admin' if user.admin else 'User'} {user.username}")
        if not use_json:
            flash(f"Disabled {user.username}.", "success")
            return redirect("/users")
        return jsonify({"status": "success", "message": f"Disabled {user.username}."})
    else:
        if not use_json:
            flash("Invalid change.", "error")
            return redirect("/users")
        return jsonify({"status": "error", "message": "Invalid change."}), 400
