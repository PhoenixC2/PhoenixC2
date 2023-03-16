import os
import unittest

from phoenixc2.server.commander.commander import Commander
from phoenixc2.server.web import create_web


class StagerTest(unittest.TestCase):
    def setUp(self):
        os.environ["PHOENIX_TEST"] = "true"
        self.app = create_web(Commander())
        self.client = self.app.test_client()

    def test_get_stagers_json(self):
        response = self.client.get("/stagers?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, True)

    def test_get_stagers(self):
        response = self.client.get("/stagers", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, False)

    def test_get_listener(self):
        response = self.client.get("/stagers/1?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, True)


if __name__ == "__main__":
    unittest.main()
