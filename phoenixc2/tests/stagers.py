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
        response = self.client.get("/stagers?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, True)

    def test_get_stagers(self):
        response = self.client.get("/stagers", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, False)

    def test_get_single_stager(self):
        response = self.client.get("/stagers/1?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, True)

    def test_stager_simulation(self):
        # Create a stager
        data = {
            "name": "test",
            "listener": 1,
            "payload": "python",
        }
        response = self.client.post("/stagers/add", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 201, "Failed to create stager")
        stager = response.json["stager"]
        self.assertEqual(stager["name"], "test", "Wrong stager name")

        # Edit a stager
        data = {
            "name": "testchange",
        }
        response = self.client.put("/stagers/1/edit", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Failed to edit stager")

        # Download a stager
        response = self.client.get("/stagers/1/download", follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Failed to download stager")

        # Delete a stager
        response = self.client.delete("/stagers/1/remove", follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Failed to delete stager")


if __name__ == "__main__":
    unittest.main()
