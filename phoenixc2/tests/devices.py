import unittest
from phoenixc2.development.database import change_to_memory_database


class DevicesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        change_to_memory_database()
        from phoenixc2.server.commander.commander import Commander
        from phoenixc2.server.api import create_api

        cls.app = create_api(Commander())
        cls.client = cls.app.test_client()

    def test_list_devices(self):
        response = self.client.get("/api/devices/")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
