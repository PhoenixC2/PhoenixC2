from Utils import *

stagers = Blueprint("stagers", __name__, url_prefix="/stagers")

@stagers.route("/")
def index():
    return render_template("listeners.html")

@stagers.route("/add", methods=["GET"])
def get_add():
    return render_template("add_listener.html")

@stagers.route("/add", methods=["POST"])
def post_add():
    # TODO: Add Stager
    return "Not implemented yet"

@stagers.route("/remove", methods=["POST"])
def post_add():
    # TODO: Remove Stager
    return "Not implemented yet"

@stagers.route("/edit", methods=["PUT"])
def post_add():
    # TODO: Edit Stager
    return "Not implemented yet"
