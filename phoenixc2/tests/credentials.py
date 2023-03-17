import unittest
from phoenixc2.development.database import change_to_memory_database


class CredentialsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        change_to_memory_database()
        from phoenixc2.server.commander.commander import Commander
        from phoenixc2.server.web import create_web

        cls.app = create_web(Commander())
        cls.client = cls.app.test_client()

    def test_credentials(self):
        response = self.client.get("/credentials?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        self.assertEqual(response.json["status"], "success")


if __name__ == "__main__":
    unittest.main()
