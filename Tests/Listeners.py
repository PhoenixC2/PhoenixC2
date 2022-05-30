import unittest
import requests as r

# Test the Authentication Endpoints of the API
class Authtest(unittest.TestCase):
    url = 'http://localhost:8080/auth/'
        
    def test_successfull_login(self):
        response = r.post(self.url + "login?json=true", data={'username': 'phoenix', 'password': 'phoenix'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
    def test_failed_login(self):
        response = r.post(self.url + "login?json=true", data={'username': 'phoenix', 'password': 'notphoenix'}, params={'json': True})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['status'], 'error')
if __name__ == '__main__':
    unittest.main()
