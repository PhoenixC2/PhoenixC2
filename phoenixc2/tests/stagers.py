import unittest
from phoenixc2.development.database import change_to_memory_database


class StagerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        change_to_memory_database()
        from phoenixc2.server.commander.commander import Commander
        from phoenixc2.server.web import create_web
        from phoenixc2.server.utils.admin import recreate_super_user

        recreate_super_user()
        cls.app = create_web(Commander())
        cls.client = cls.app.test_client()

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

    def test_stager_simulation(self):
        # Create a listener
        post_data = {
            "type": "http-reverse",
            "name": "test",
        }
        response = self.client.post(
            "/listeners/add", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 201, "Failed to create listener")
        listener = response.json["listener"]
        self.assertEqual(listener["name"], "test", "Wrong listener name")
        self.assertEqual(listener["type"], "http-reverse", "Wrong listener type")

        # Create a stager
        post_data = {
            "name": "test",
            "listener": 1,
        }
        response = self.client.post(
            "/stagers/add", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 201, "Failed to create stager")
        stager = response.json["stager"]
        self.assertEqual(stager["name"], "test", "Wrong stager name")

        # Edit a stager
        post_data = {
            "name": "testchange",
        }
        response = self.client.put(
            "/stagers/1/edit", data=post_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200, "Failed to edit stager")

        # Download a stager
        response = self.client.get("/stagers/1/download", follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Failed to download stager")

        # Delete a stager
        response = self.client.delete("/stagers/1/remove", follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Failed to delete stager")


if __name__ == "__main__":
    unittest.main()
