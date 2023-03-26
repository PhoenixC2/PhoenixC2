import unittest
from phoenixc2.development.database import change_to_memory_database


class ListenerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        change_to_memory_database()
        from phoenixc2.server.commander.commander import Commander
        from phoenixc2.server.web import create_web

        cls.app = create_web(Commander())
        cls.client = cls.app.test_client()

    def test_get_listeners_json(self):
        response = self.client.get("/listeners?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    def test_get_listeners(self):
        response = self.client.get("/listeners", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.is_json)

    def test_listener_simulation(self):
        data = {
            "type": "http-reverse",
            "name": "test",
        }
        response = self.client.post("/listeners/add", data=data, follow_redirects=True)
        self.assertTrue(response.is_json)
        self.assertEqual(response.status_code, 201, response.json["message"])
        listener = response.json["listener"]
        self.assertEqual(listener["name"], "test", "Wrong listener name")
        self.assertEqual(listener["type"], "http-reverse", "Wrong listener type")

        data = {
            "name": "testchange",
        }
        response = self.client.put(
            "/listeners/1/edit", data=data, follow_redirects=True
        )
        self.assertTrue(response.is_json)
        self.assertEqual(response.status_code, 200, response.json["message"])

        response = self.client.delete(
            f"/listeners/{listener['id']}/remove", follow_redirects=True
        )
        self.assertEqual(response.status_code, 200, response.json["message"])


if __name__ == "__main__":
    unittest.main()
