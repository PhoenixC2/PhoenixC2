import unittest
from phoenixc2.development.database import change_to_memory_database, generate_stager


class BypassTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        change_to_memory_database()
        from phoenixc2.server.commander.commander import Commander
        from phoenixc2.server.api import create_api

        cls.commander = Commander()
        cls.app = create_api(cls.commander)
        cls.client = cls.app.test_client()
        cls.stager = generate_stager()

    def test_get_bypasses(self):
        response = self.client.get("/bypasses", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.is_json)

    def test_get_bypasses_json(self):
        response = self.client.get("/bypasses?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    def test_run_single_bypass(self):
        data = {
            "stager": self.stager.id,
        }
        response = self.client.post(
            "/bypasses/run/encoders/base64", follow_redirects=True, data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.is_json)

    def test_get_bypass_chains(self):
        response = self.client.get("/bypasses/chains", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.is_json)

    def test_get_bypass_chains_json(self):
        response = self.client.get("/bypasses/chains?json=true", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    def test_chain_simulation(self):
        data = {
            "name": "test_chain",
            "description": "test chain description",
        }

        response = self.client.post(
            "/bypasses/chains/add", follow_redirects=True, data=data
        )
        self.assertEqual(response.status_code, 201, "Failed to add chain")

        chain = response.json["chain"]

        data = {
            "name": "test_chain_edit",
        }

        response = self.client.put(
            f"/bypasses/chains/{chain['id']}/edit", follow_redirects=True, data=data
        )
        self.assertEqual(response.status_code, 200, "Failed to edit chain")

        data = {
            "category": "encoders",
            "name": "base64",
        }

        response = self.client.post(
            f"/bypasses/chains/{chain['id']}/bypass/add",
            follow_redirects=True,
            data=data,
        )
        self.assertEqual(response.status_code, 201, "Failed to add bypass to chain")

        data = {
            "category": "encoders",
            "name": "hex",
        }

        response = self.client.post(
            f"/bypasses/chains/{chain['id']}/bypass/add",
            follow_redirects=True,
            data=data,
        )
        self.assertEqual(
            response.status_code, 201, "Failed to add second bypass to chain"
        )

        data = {
            "position": 1,
        }
        response = self.client.put(
            f"/bypasses/chains/{chain['id']}/bypass/2/move",
            follow_redirects=True,
            data=data,
        )
        self.assertEqual(response.status_code, 200, "Failed to move bypass up in chain")

        response = self.client.get(
            f"/bypasses/chains/{chain['id']}?json=true", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200, "Failed to get chain")
        update_chain = response.json["chain"]
        self.assertEqual(update_chain["bypasses"][0]["name"], "Hex")
        self.assertEqual(update_chain["bypasses"][1]["name"], "Base64")

        data = {
            "stager": self.stager.id,
        }
        response = self.client.post(
            f"/bypasses/chains/{chain['id']}/run", follow_redirects=True, data=data
        )
        self.assertEqual(response.status_code, 200, "Failed to run chain on stager")

        response = self.client.delete(
            f"/bypasses/chains/{chain['id']}/remove", follow_redirects=True
        )
        self.assertEqual(response.status_code, 200, "Failed to delete chain")


if __name__ == "__main__":
    unittest.main()
