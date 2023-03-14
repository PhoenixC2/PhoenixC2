from phoenixc2.server.web import create_web
from phoenixc2.server.commander import Commander
import unittest
import os


class DashboardTest(unittest.TestCase):
    def setUp(self):
        os.environ["PHOENIX_TEST"] = "true"
        self.app = create_web(Commander())
        self.client = self.app.test_client()

    def testGetData(self):
        response = self.client.get("/dashboard?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, True)


if __name__ == "__main__":
    unittest.main()
