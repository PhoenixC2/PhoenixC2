import unittest
import requests as r
# Test the Authentication Endpoints of the API
class AuthTest(unittest.TestCase):
    def __init__(self):
        self.url = 'http://localhost:8080/listeners/'
        self.headers = {'Content-Type': 'application/www-form-urlencoded'}
    def successfull_login(self):
        response = r.post(self.url, data={'username': 'phoenix', 'password': 'phoenix'}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        #self.assertEqual(response.json()['status'], 'success')
    def failed_login(self):
        response = r.post(self.url, data={'username': 'phoenix', 'password': 'notphoenix'}, headers=self.headers)
        self.assertEqual(response.status_code, 401)
        #self.assertEqual(response.json()['status'], 'error')
if __name__ == '__main__':
    unittest.main()
