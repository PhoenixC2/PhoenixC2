import requests
class Communication(requests.Session):
    """Communication class for the client"""
    def __init__(self, url):
        super().__init__()
        self.headers['Content-Type'] = 'application/www-form-urlencoded'
        self.url = url
    def login(self, username, password):
        """Login to the server"""
        data = {'username': username, 'password': password}
        res = self.post(self.url + '/auth/login', data=data, headers=self.headers)
        self.cookies.update(res.cookies)
        return True if res.status_code == 200 else False
    def user(self):
        """Get the user"""
        res = self.get(self.url + '/auth/user')
        return res.json()
    