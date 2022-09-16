from typing import TYPE_CHECKING
from Database import db_session, UserModel, ListenerModel
from flask import Blueprint, render_template
from Utils.web import get_current_user, authorized

if TYPE_CHECKING:
    from Commander import Commander


def routes_bp(commander: "Commander") -> Blueprint:

    routes_bp = Blueprint("routes", __name__, url_prefix="/auth")

    @routes_bp.route("/home")
    @routes_bp.route("/dashboard")
    @routes_bp.route("/")
    @authorized
    def index():
        listeners = db_session.query(ListenerModel).all()
        
        active_devices = commander.active_handlers_count
        active_listeners = commander.active_listeners_count
        active_users = 0
        for user in db_session.query(UserModel).all():
            if user.activity_status == "active":
                active_users += 1
        return render_template(
            "dashboard.j2",
            user=get_current_user(),
            active_devices=active_devices,
            active_listeners=active_listeners,
            active_users=active_users)

    return routes_bp