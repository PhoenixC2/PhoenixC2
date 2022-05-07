from Utils import *
from Creator import options, formats, encoders
misc = Blueprint("mics", __name__, url_prefix="/misc")

@misc.route("/options")
def get_options():
    return jsonify(options)

@misc.route("/formats")
def get_formats():
    return jsonify(formats)

@misc.route("/encoders")
def get_encoders():
    return jsonify(encoders)

@misc.route("/version")
def get_phoenix():
    return jsonify({"version": "1.0.0"})