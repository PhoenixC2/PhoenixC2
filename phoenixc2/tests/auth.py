import unittest
from phoenixc2.development.database import change_to_memory_database


class TestAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        change_to_memory_database()
        # imports here because of the database change
        from phoenixc2.server.api import create_api
        from phoenixc2.server.commander.commander import Commander
        from phoenixc2.server.database import UserModel, Session

        cls.app = create_api(Commander())
        cls.client = cls.app.test_client()
        cls.user = UserModel.create(
            "test",
            "testtest123",
            True,
            False,
        )
        Session.commit()

    # cant test login because the password always changes

    def test_login(self):
        response = self.client.post(
            "/api/auth/login",
            json=dict(username="test", password="testtest123"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["user"]["admin"])

    def test_failed_login(self):
        response = self.client.post(
            "/api/auth/login",
            json=dict(username="test", password="wrong"),
        )
        self.assertEqual(response.status_code, 401)

    def test_logout(self):
        response = self.client.get("/api/auth/logout")
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        from phoenixc2.server.database import Session

        Session.delete(cls.user)


if __name__ == "__main__":
    unittest.main()
