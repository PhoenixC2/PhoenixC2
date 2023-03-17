import unittest
from phoenixc2.development.database import change_to_memory_database


class TestAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        change_to_memory_database()
        # imports here because of the database change
        from phoenixc2.server.web import create_web
        from phoenixc2.server.commander.commander import Commander
        from phoenixc2.server.database import UserModel, Session

        cls.app = create_web(Commander())
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
            "/auth/login?json=true",
            data=dict(username="test", password="testtest123"),
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        self.assertTrue(response.json["user"]["admin"])

    def test_failed_login(self):
        response = self.client.post(
            "/auth/login",
            data=dict(username="test", password="wrong"),
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 401)

    def test_logout(self):
        response = self.client.get("/auth/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        from phoenixc2.server.database import Session

        Session.delete(cls.user)


if __name__ == "__main__":
    unittest.main()
