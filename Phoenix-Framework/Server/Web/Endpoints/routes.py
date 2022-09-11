from flask import Blueprint, render_template
from Utils.web import get_current_user
from Database import db_session, DeviceModel, ListenerModel, StagerModel
routes_bp = Blueprint("routes", __name__, url_prefix="/auth")


@routes_bp.route("/home")
@routes_bp.route("/index")
@routes_bp.route("/")
def index():
    devices = db_session.query(DeviceModel).all()
    listeners = db_session.query(ListenerModel).all()
    stagers = db_session.query(StagerModel).all()
    return render_template(
        "index.j2",
        user=get_current_user(),
        devices=devices,
        listeners=listeners,
        stagers=stagers)
