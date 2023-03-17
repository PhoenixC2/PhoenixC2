import unittest
from phoenixc2.development.database import change_to_memory_database


class LogsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        change_to_memory_database()
        from phoenixc2.server.commander.commander import Commander
        from phoenixc2.server.web import create_web

        cls.app = create_web(Commander())
        cls.client = cls.app.test_client()

    def test_logs(self):
        response = self.client.get("/logs?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "success")
        self.assertEqual(response.is_json, True)

    def test_clear_logs(self):
        response = self.client.delete("/logs/all/clear", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "success")
        self.assertEqual(response.is_json, True)


if __name__ == "__main__":
    unittest.main()
