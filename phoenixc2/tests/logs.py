from phoenixc2.server.web import create_web
from phoenixc2.server.commander import Commander
import unittest
import os

class DashboardTest(unittest.TestCase):

    def setUp(self):
        os.environ["PHOENIX_TEST"] = "true"
        self.app = create_web(Commander())
        self.client = self.app.test_client()