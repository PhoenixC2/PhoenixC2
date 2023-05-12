import unittest
from phoenixc2.development.database import change_to_memory_database


class MiscTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        change_to_memory_database()
        from phoenixc2.server.commander.commander import Commander
        from phoenixc2.server.api import create_api

        cls.app = create_api(Commander())
        cls.client = cls.app.test_client()

    def test_get_network_interfaces(self):
        response = self.client.get("/api/misc/interfaces")
        self.assertEqual(response.status_code, 200)

    def test_get_downloads(self):
        response = self.client.get("/api/misc/downloads")
        self.assertEqual(response.status_code, 404)

    def test_post_clear_uploads(self):
        response = self.client.delete("/api/misc/uploads/clear")
        self.assertEqual(response.status_code, 200)

    def test_post_clear_downloads(self):
        response = self.client.delete("/api/misc/downloads/clear")
        self.assertEqual(response.status_code, 200)

    def test_post_clear_stagers(self):
        response = self.client.delete("/api/misc/stagers/clear")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
