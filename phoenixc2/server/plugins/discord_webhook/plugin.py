import requests
from phoenixc2.server.plugins.base import ConnectionEventPlugin

IMAGE_URL = (
    "https://raw.githubusercontent.com/screamz2k/PhoenixC2/main/pages/images/logo.png"
)


class Plugin(ConnectionEventPlugin):
    name = "Discord Webhook Plugin"
    description = "Sends a message to a Discord webhook when a new device connects."
    required_dependencies = [("requests", "latest")]

    @staticmethod
    def execute(device, config):
        if "webhook" not in config:
            raise KeyError("webhook_id not in config")
        embed = {
            "title": "New Device Connected",
            "type": "rich",
            "description": f"Device {device.name} connected to the server.",
            "image": {
                "url": IMAGE_URL,
            },
            "color": int("ff9a51", 16),
            "fields": [
                {"name": "Name", "value": device.name, "inline": True},
                {"name": "Hostname", "value": device.hostname, "inline": True},
                {"name": "Address", "value": device.address, "inline": True},
                {"name": "OS", "value": device.os, "inline": True},
                {"name": "User", "value": device.user, "inline": True},
                {
                    "name": "Admin",
                    "value": "✅" if device.admin else "❌",
                    "inline": True,
                },
            ],
        }
        response = requests.post(
            config["webhook"],
            json={
                "username": "PhoenixC2",
                "avatar_url": IMAGE_URL,
                "embeds": [embed],
            },
        )
        response.raise_for_status()
