from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from flask import Blueprint, render_template, request

import phoenixc2
import phoenixc2.server as avl
from phoenixc2.server.database import DeviceModel, OperationModel, Session, UserModel
from phoenixc2.server.utils.misc import Status

if TYPE_CHECKING:
    from phoenixc2.server.commander.commander import Commander


def dashboard_bp(commander: "Commander") -> Blueprint:
    dashboard_bp = Blueprint("routes", __name__, url_prefix="/")

    @dashboard_bp.route("/home")
    @dashboard_bp.route("/dashboard")
    @dashboard_bp.route("/info")
    @dashboard_bp.route("/")
    @UserModel.authenticated
    def get_index():
        use_json = request.args.get("json", "").lower() == "true"
        devices: list[DeviceModel] = Session.query(DeviceModel).all()
        operations: list[OperationModel] = Session.query(OperationModel).all()
        # get count of connections from today
        connections_today = (
            Session.query(DeviceModel)
            .filter(DeviceModel.connection_time >= datetime.now() - timedelta(days=1))
            .count()
        )
        # get count of connections from the last hour
        connections_last_hour = (
            Session.query(DeviceModel)
            .filter(DeviceModel.connection_time >= datetime.now() - timedelta(hours=1))
            .count()
        )
        active_users = (
            Session.query(UserModel)
            .filter(UserModel.last_activity >= datetime.now() - timedelta(minutes=5))
            .count()
        )
        if use_json:
            return {
                "status": Status.Success,
                "version": phoenixc2.__version__,
                "devices": len(devices),
                "operations": len(operations),
                "active_devices": len(commander.active_handlers),
                "active_listeners": len(commander.active_listeners),
                "active_users": active_users,
                "connections_last_hour": connections_last_hour,
                "connections_today": connections_today,
                "installed_kits": avl.INSTALLED_KITS,
                "installed_loaders": avl.INSTALLED_LOADERS,
            }
        return render_template(
            "dashboard.j2",
            devices=devices,
            operations=operations,
            active_devices=len(commander.active_handlers),
            active_listeners=len(commander.active_listeners),
            active_users=active_users,
            connections_last_hour=connections_last_hour,
            connections_today=connections_today,
        )

    return dashboard_bp
