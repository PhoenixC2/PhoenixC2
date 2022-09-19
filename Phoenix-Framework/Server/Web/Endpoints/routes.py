from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from Database import DeviceModel, UserModel, db_session
from flask import Blueprint, render_template
from Utils.web import authorized, get_current_user

if TYPE_CHECKING:
    from Commander import Commander


def routes_bp(commander: "Commander") -> Blueprint:

    routes_bp = Blueprint("routes", __name__, url_prefix="/auth")
    @routes_bp.route("/home")
    @routes_bp.route("/dashboard")
    @routes_bp.route("/")
    @authorized
    def index():
        devices: list[DeviceModel] = db_session.query(DeviceModel).all()
        connections_last_hour = 0
        connections_today = 0
        for device in devices:
            delta = datetime.now() - device.connection_date
            if delta.seconds / 60 <= 60:
                connections_last_hour += 1
                connections_today += 1
            elif datetime.date(device.connection_date) == datetime.date(datetime.today()):
                connections_today += 1
            

        active_devices = commander.active_handlers_count
        active_listeners = commander.active_listeners_count
        active_users = 0
        for user in db_session.query(UserModel).all():
            if user.activity_status == "online":
                active_users += 1
        
        return render_template(
            "dashboard.j2",
            user=get_current_user(),
            devices=devices,
            active_devices=active_devices,
            active_listeners=active_listeners,
            active_users=active_users,
            connections_last_hour=connections_last_hour,
            connections_today=connections_today)

    return routes_bp