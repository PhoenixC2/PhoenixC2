import unittest

import requests as r

# Test the Listener Endpoints of the API

json_param = "?json=true"
listener_id = None


class ListenerTest(unittest.TestCase):
    url = "http://localhost:8080/listeners/"
    session = r.Session()

    def test1_get_listeners(self):
        print("Getting Listeners")
        response = self.session.get(self.url + json_param)
        self.assertEqual(response.status_code, 200)

    def test2_create_listener(self):
        global listener_id
        print("Creating Listener")
        data = {
            "name": "test",
            "type": "http/reverse",
            "address": "0.0.0.0",
            "port": 9999,
            "ssl": True,
            "enabled": True,
            "limit": 0,
        }
        response = self.session.post(self.url + "/add" + json_param, data=data)
        self.assertEqual(response.status_code, 201)
        print(response.json())
        listener_id = str(response.json()["listener"]["id"])

    def test3_start_listener(self):
        print("Starting Listener")
        print(listener_id)
        response = self.session.post(
            self.url + listener_id + "/start" + json_param, data={"id": 1}
        )
        self.assertEqual(response.status_code, 200)

    def test4_restart_listener(self):
        print("Restarting Listener")
        response = self.session.post(
            self.url + listener_id + "/restart" + json_param, data={"id": 1}
        )
        self.assertEqual(response.status_code, 200)

    def test5_stop_listener(self):
        print("Stopping Listener")
        response = self.session.post(
            self.url + listener_id + "/stop" + json_param, data={"id": 1}
        )
        self.assertEqual(response.status_code, 200)

    def test6_remove_listener(self):
        print("Removing Listener")
        response = self.session.delete(
            self.url + listener_id + "/remove" + json_param, data={"id": 1}
        )
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
