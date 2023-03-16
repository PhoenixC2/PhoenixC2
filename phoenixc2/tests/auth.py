import unittest

from phoenixc2.server.commander.commander import Commander
from phoenixc2.server.web import create_web


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.app = create_web(Commander())
        self.client = self.app.test_client()

    # cant test login because the password always changes

    def test_failed_login(self):
        response = self.client.post(
            "/auth/login",
            data=dict(username="wrong", password="wrong"),
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 401)

    def test_logout(self):
        response = self.client.get("/auth/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
