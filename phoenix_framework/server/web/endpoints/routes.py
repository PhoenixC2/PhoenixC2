from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from flask import Blueprint, render_template

from phoenix_framework.server.database import DeviceModel, Session, TaskModel, UserModel
from phoenix_framework.server.utils.web import authorized

if TYPE_CHECKING:
    from phoenix_framework.server.commander import Commander

import json

json.dumps


def routes_bp(commander: "Commander") -> Blueprint:

    routes_bp = Blueprint("routes", __name__, url_prefix="/auth")

    @routes_bp.route("/home")
    @routes_bp.route("/dashboard")
    @routes_bp.route("/")
    @authorized
    def index():
        devices: list[DeviceModel] = Session.query(DeviceModel).all()
        # get count of connections from today
        connections_today = (
            Session.query(DeviceModel)
            .filter(DeviceModel.connection_date >= datetime.now() - timedelta(days=1))
            .count()
        )
        # get count of connections from the last hour
        connections_last_hour = (
            Session.query(DeviceModel)
            .filter(DeviceModel.connection_date >= datetime.now() - timedelta(hours=1))
            .count()
        )
        active_users = (
            Session.query(UserModel)
            .filter(UserModel.last_activity >= datetime.now() - timedelta(minutes=5))
            .count()
        )

        return render_template(
            "dashboard.j2",
            devices=devices,
            active_devices=len(commander.active_handlers),
            active_listeners=len(commander.active_listeners),
            active_users=active_users,
            connections_last_hour=connections_last_hour,
            connections_today=connections_today,
        )

    return routes_bp
