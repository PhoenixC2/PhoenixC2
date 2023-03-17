import unittest
from phoenixc2.development.database import change_to_memory_database


class ModuleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        change_to_memory_database()
        from phoenixc2.server.commander.commander import Commander
        from phoenixc2.server.web import create_web

        cls.app = create_web(Commander())
        cls.client = cls.app.test_client()

    def test_get_modules(self):
        response = self.client.get("/modules", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, False)

    def test_get_modules_json(self):
        response = self.client.get("/modules?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.is_json, True)


if __name__ == "__main__":
    unittest.main()
