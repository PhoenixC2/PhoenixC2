import unittest
from phoenixc2.development.database import change_to_memory_database


class UserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        change_to_memory_database()
        from phoenixc2.server.commander.commander import Commander
        from phoenixc2.server.web import create_web

        cls.app = create_web(Commander())
        cls.client = cls.app.test_client()

    def test_get_listeners_json(self):
        response = self.client.get("/users?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, True)

    def test_get_listeners(self):
        response = self.client.get("/users", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, False)

    def test_user_simulation(self):
        # Create a user
        post_data = {
            "username": "test",
            "password": "testtest123",
            "admin": True,
            "disabled": False,
        }
        response = self.client.post("/users/add", data=post_data, follow_redirects=True)
        self.assertTrue(response.is_json)
        self.assertEqual(response.status_code, 201, response.json["message"])

        # Get profile picture
        response = self.client.get("/users/1/picture", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Update the user
        post_data = {"username": "testchanged"}
        response = self.client.put(
            "/users/1/edit", data=post_data, follow_redirects=True
        )
        self.assertTrue(response.is_json)
        self.assertEqual(response.status_code, 200, response.json["message"])


if __name__ == "__main__":
    unittest.main()
