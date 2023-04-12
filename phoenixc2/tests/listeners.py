import unittest
from phoenixc2.development.database import change_to_memory_database


class ListenerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        change_to_memory_database()
        from phoenixc2.server.commander.commander import Commander
        from phoenixc2.server.api import create_api

        cls.app = create_api(Commander())
        cls.client = cls.app.test_client()

    def test_get_listeners(self):
        response = self.client.get("/api/listeners/")
        self.assertEqual(response.status_code, 200)

    def test_listener_simulation(self):
        data = {
            "type": "http-reverse",
            "name": "test",
        }
        response = self.client.post("/api/listeners/add", json=data)
        self.assertEqual(response.status_code, 201, response.json["message"])
        listener = response.json["listener"]
        self.assertEqual(listener["name"], "test", "Wrong listener name")
        self.assertEqual(listener["type"], "http-reverse", "Wrong listener type")

        data = {
            "name": "testchange",
        }
        response = self.client.put("/api/listeners/1/edit", json=data)
        self.assertEqual(response.status_code, 200, response.json["message"])

        response = self.client.delete(f"/api/listeners/{listener['id']}/remove")
        self.assertEqual(response.status_code, 200, response.json["message"])


if __name__ == "__main__":
    unittest.main()
