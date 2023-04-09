import requests
from phoenixc2.server.utils.ui import log
from phoenixc2.server.utils.misc import Status
import phoenixc2


def check_for_update() -> bool:
    try:
        response = requests.get(
            "https://api.github.com/repos/screamz2k/phoenixc2/releases/latest"
        )
        response.raise_for_status()
    except requests.exceptions.RequestException:
        log("Error checking for update.", Status.Danger)
        return False

    if response.status_code == 200:
        latest_version = response.json()["tag_name"]
        if latest_version[1:] != phoenixc2.__version__:
            log(f"Update available: {latest_version}", Status.Warning)
            return True
        else:
            log("PhoenixC2 is up to date.", Status.Success)
            return False
    else:
        log(f"Error checking for update: {response.status_code}", Status.Danger)
        return False
