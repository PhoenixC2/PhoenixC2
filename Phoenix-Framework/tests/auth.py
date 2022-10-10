import unittest
import requests as r

USERNAME = "phoenix"
PASSWORD = "phoenix"

# Test the Authentication Endpoints of the API

json_param = '?json=true'
class Authtest(unittest.TestCase):
    url = 'http://localhost:8080/auth/'
    session = r.Session()

    def test_login(self):
        data = {'username': USERNAME, 'password': PASSWORD}
        response = self.session.post(self.url + 'login' + json_param, data=data)
        self.assertEqual(response.status_code, 200)

    def test_fail_login(self):
        data = {'username': USERNAME, 'password': 'wrong'}
        response = self.session.post(self.url + 'login' + json_param, data=data)
        self.assertEqual(response.status_code, 401)
    
    def test_logout(self):
        self.session.get(self.url + 'login' + json_param)
        response = self.session.get(self.url + 'logout' + json_param)
        self.assertEqual(response.status_code, 200)
    

if __name__ == '__main__':
    unittest.main()