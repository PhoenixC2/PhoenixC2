import unittest
import requests as r

# Test the Frontend
routes = ["dashboard", "listeners", "stagers", "devices", "users", "logs", "tasks", "settings", "credentials", "loaders", "modules"]
class RouteTest(unittest.TestCase):
    url = 'http://localhost:8080/'
    session = r.Session()

    def test_get_routes(self):
        for route in routes:
            print("Getting " + route)
            response = self.session.get(self.url + route)
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()