from requests import Session, Response
from .user import User


class Server:
    """Represents the server"""

    _session: Session
    _url: str
    user: User

    def __init__(self, url: str) -> None:
        self._url = url
        self._session = Session()

    def credentials_login(self, username: str, password: str) -> None:
        """Login to the server with credentials"""
        res = self.request(
            "auth/login", "post", data={"username": username, "password": password}
        )

        try:
            res.raise_for_status()
        except Exception as e:
            raise Exception("Invalid credentials") from e

        self.user = User(self, res.json()["user"])

    def key_login(self, key: str) -> None:
        """Login to the server with an API key"""
        res = self.request("login", "post", headers={"Api-Key": key})

        try:
            res.raise_for_status()
        except Exception as e:
            raise Exception("Invalid key") from e

        self.user = User(self, res.json()["user"])

    def request(self, endpoint: str, method: str = "get", **kwargs) -> Response:
        """Make a request to the server"""
        url = self._url + "/" + endpoint + "?json=true"
        response = self._session.request(method, url, **kwargs)
        return response
