from flask import Blueprint, render_template
routes_bp = Blueprint("routes", __name__, url_prefix="/auth")


@routes_bp.route("/home")
@routes_bp.route("/index")
@routes_bp.route("/")
def index():
    return render_template("index.html")
