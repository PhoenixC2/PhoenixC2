import unittest
import requests as r

# Test the Listener Endpoints of the API

json_param = '?json=true'

class ListenerTest(unittest.TestCase):
    url = 'http://localhost:8080/listeners/'
    session = r.Session()
    listener_id = "1"

    def test_get_listeners_1(self):
        print("Getting Listeners")
        response = self.session.get(self.url + json_param)
        self.assertEqual(response.status_code, 200)

    def test_create_listener_2(self):
        print("Creating Listener")
        data = {
            'name': 'test',
            'type': "http/reverse",
            'address': '0.0.0.0',
            'port': 9999,
            'ssl': True,
            'enabled': True,
            'limit': 0,
        }
        response = self.session.post(self.url + "/add" + json_param, data=data)
        self.assertEqual(response.status_code, 201)
        self.listener_id = str(response.json()['id'])


    def test_start_listener_3(self):
        print("Starting Listener")
        response = self.session.post(self.url + self.listener_id + "/start" + json_param, data={'id': 1})
        self.assertEqual(response.status_code, 200)
    
    def test_restart_listener_4(self):
        print("Restarting Listener")
        response = self.session.post(self.url + self.listener_id + "/restart" + json_param, data={'id': 1})
        self.assertEqual(response.status_code, 200)
    
    def test_stop_listener_5(self):
        print("Stopping Listener")
        response = self.session.post(self.url + self.listener_id + "/stop" + json_param, data={'id': 1})
        self.assertEqual(response.status_code, 200)
    
    
    def test_remove_listener_6(self):
        print("Removing Listener")
        response = self.session.delete(self.url + self.listener_id + "/remove" + json_param, data={'id': 1})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()