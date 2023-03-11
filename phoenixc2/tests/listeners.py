from phoenixc2.server.web import create_web
from phoenixc2.server.commander import Commander
import unittest
import os

class ListenerTest(unittest.TestCase):
    def setUp(self):
        os.environ["PHOENIX_TEST"] = "true"
        self.app = create_web(Commander())
        self.client = self.app.test_client()

    def test_get_listeners_json(self):
        response = self.client.get("/listeners?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, True)

    def test_get_listeners(self):
        response = self.client.get("/listeners", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, False)

    def test_get_listener(self):
        response = self.client.get("/listeners/1?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, True)

if __name__ == "__main__":
    unittest.main()