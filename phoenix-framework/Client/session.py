from requests import Session


class CliSession(Session):
    """The Requests session to handle authorization and communication to the server"""

    def __init__(self, server: str) -> None:
        super().__init__()
        self.server = server
        self.api_key = ""
    def login_pass(self, user:str, password:str):
        """Login using username and password"""
        ...
    
    def login_key(self, key:str):
        """Login using Api-key"""
        ...
    
