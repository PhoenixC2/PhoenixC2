from Utils import *

listeners = Blueprint("listeners", __name__, url_prefix="/listeners")

@listeners.route("/")
def index():
    return render_template("listeners.html")

@listeners.route("/add", methods=["GET"])
def get_add():
    return render_template("add_listener.html")

@listeners.route("/add", methods=["POST"])
def post_add():
    # TODO: Add listener
    return "Not implemented yet"

@listeners.route("/remove", methods=["POST"])
def post_add():
    # TODO: Remove listener
    return "Not implemented yet"

@listeners.route("/edit", methods=["PUT"])
def post_add():
    # TODO: Edit listener
    return "Not implemented yet"
