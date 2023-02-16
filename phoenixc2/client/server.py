from requests import Session, request

class Server:
    """Represents the server"""
    _session: Session
    _url: str 

    def __init__(self, url: str) -> None:
        self._url = url
        self._session = Session()