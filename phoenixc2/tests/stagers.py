import unittest
from phoenixc2.development.database import change_to_memory_database, generate_listener


class StagerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        change_to_memory_database()
        from phoenixc2.server.commander.commander import Commander
        from phoenixc2.server.api import create_api
        from phoenixc2.server.utils.admin import recreate_super_user

        recreate_super_user()
        cls.app = create_api(Commander())
        cls.client = cls.app.test_client()
        cls.listener = generate_listener()

    def test_get_stagers_json(self):
        response = self.client.get("/api/stagers/?json=true")
        self.assertEqual(response.status_code, 200)

    def test_get_stagers(self):
        response = self.client.get("/api/stagers/")
        self.assertEqual(response.status_code, 200)

    def test_get_single_stager(self):
        response = self.client.get("/api/stagers/1?json=true")
        self.assertEqual(response.status_code, 200)

    def test_stager_simulation(self):
        # Create a stager
        data = {
            "name": "test",
            "listener": 1,
            "payload": "python",
        }
        response = self.client.post("/api/stagers/add", json=data)
        self.assertEqual(response.status_code, 201, "Failed to create stager")
        stager = response.json["stager"]
        self.assertEqual(stager["name"], "test", "Wrong stager name")

        # Edit a stager
        data = {
            "name": "testchange",
        }
        response = self.client.put("/api/stagers/1/edit", json=data)
        self.assertEqual(response.status_code, 200, "Failed to edit stager")

        # Download a stager
        response = self.client.get("/api/stagers/1/download")
        self.assertEqual(response.status_code, 200, "Failed to download stager")

        # Delete a stager
        response = self.client.delete("/api/stagers/1/remove")
        self.assertEqual(response.status_code, 200, "Failed to delete stager")


if __name__ == "__main__":
    unittest.main()
