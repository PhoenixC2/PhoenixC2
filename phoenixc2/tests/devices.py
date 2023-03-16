import os
import unittest

from phoenixc2.server.commander.commander import Commander
from phoenixc2.server.web import create_web


class DevicesTest(unittest.TestCase):
    def setUp(self):
        os.environ["PHOENIX_TEST"] = "true"
        self.app = create_web(Commander())
        self.client = self.app.test_client()

    def test_list_devices(self):
        response = self.client.get("/devices?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, True)


if __name__ == "__main__":
    unittest.main()
