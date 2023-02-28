from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import Server

class User:
    server : "Server"

    def __init__(self, server: "Server", data: dict) -> None:
        self.server = server
        self.id: int = data["id"]
        self.username: str = data["username"]
        self.admin: bool = data["admin"]
        self.api_key : str = data["api_key"]

    def read_messages(self) -> list:
        """Read all messages for the user"""
        return self.server.request("logs/read", "get")
    
    @staticmethod
    def get_user(server: "Server", id : int) -> "User":
        """Get a user from the server"""
        res = server.request(f"users/{id}" , "get")
        return User(server, res.json()["user"])
    