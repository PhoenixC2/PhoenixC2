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
        response = self.client.get("/api/bypasses/")
        self.assertEqual(response.status_code, 200)

    def test_run_single_bypass(self):
        response = self.client.get(
            f"/api/bypasses/run/encoders/base64?stager={self.stager.id}"
        )
        self.assertEqual(response.status_code, 200)

    def test_get_bypass_chains(self):
        response = self.client.get("/api/bypasses/chains")
        self.assertEqual(response.status_code, 200)

    def test_chain_simulation(self):
        data = {
            "name": "test_chain",
            "description": "test chain description",
        }

        response = self.client.post("/api/bypasses/chains/add", json=data)
        self.assertEqual(response.status_code, 201, "Failed to add chain")

        chain = response.json["chain"]

        data = {
            "name": "test_chain_edit",
        }

        response = self.client.put(
            f"/api/bypasses/chains/{chain['id']}/edit", json=data
        )
        self.assertEqual(response.status_code, 200, "Failed to edit chain")

        data = {
            "category": "encoders",
            "name": "base64",
        }

        response = self.client.post(
            f"/api/bypasses/chains/{chain['id']}/bypasses/add",
            json=data,
        )
        self.assertEqual(response.status_code, 201, "Failed to add bypass to chain")

        data = {
            "category": "encoders",
            "name": "hex",
        }

        response = self.client.post(
            f"/api/bypasses/chains/{chain['id']}/bypasses/add",
            json=data,
        )
        self.assertEqual(
            response.status_code, 201, "Failed to add second bypass to chain"
        )

        data = {
            "position": 1,
        }
        response = self.client.put(
            f"/api/bypasses/chains/{chain['id']}/bypasses/2/move",
            json=data,
        )
        self.assertEqual(response.status_code, 200, "Failed to move bypass up in chain")

        response = self.client.get(f"/api/bypasses/chains/{chain['id']}")

        self.assertEqual(response.status_code, 200, "Failed to get chain")
        update_chain = response.json["chain"]
        self.assertEqual(update_chain["bypasses"][0]["name"], "Hex")
        self.assertEqual(update_chain["bypasses"][1]["name"], "Base64")

        data = {
            "stager": self.stager.id,
        }
        response = self.client.get(
            f"/api/bypasses/chains/{chain['id']}/run?stager={self.stager.id}"
        )
        self.assertEqual(response.status_code, 200, "Failed to run chain on stager")

        response = self.client.delete(f"/api/bypasses/chains/{chain['id']}/remove")
        self.assertEqual(response.status_code, 200, "Failed to delete chain")


if __name__ == "__main__":
    unittest.main()
