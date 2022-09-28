import json
import unittest
import configparser
from uuid import uuid4

import requests

config = configparser.ConfigParser()
config.read('config.ini')

bool_map = {'True': True, 'False': False}
IS_LOCAL = bool_map[config['General']['Islocal']]

if IS_LOCAL:
    base_url = config['General']['Localhost']
else:
    base_url = config['General']['Remotehost']

announcement_url = base_url + '/announcement'
announcements_url = base_url + '/announcements'

headers = {
    'Content-Type': 'application/json',
    'x-api-key': config['General']['X-Api-Key'],
}

limit = 3
invalid_limit = 'q3'
test_id = 'd8651c52'

data = {
    'title': str(uuid4())[:5],
    'description': str(uuid4()),
}


def make_request(url, method='GET', data=None, params={}):
    print(f'{method} request to {url}')

    if method == 'GET':
        response = requests.get(url, headers=headers, params=params)
        print(response.url)
    if method == 'POST':
        response = requests.post(url, headers=headers, json=data)

    return response


class TestRequests(unittest.TestCase):
    def test_post_request(self):
        response = make_request(announcement_url, method='POST', data=data)
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['Message'], 'Success')
        self.assertIsNotNone(content['Item'])

    def test_get_limit_announcements_request(self):
        params = {'limit': limit}
        response = make_request(
            announcements_url, method='GET', params=params
        )
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(content['announcements'])
        self.assertEqual(len(content['announcements']), limit)

        print(
            f'Response from {response}, status_code: {response.status_code},\n'
            f'Headers: {response.headers}\n'
            f'Body: {json.loads(response.content)}\n'
        )

    def test_invalid_limit_request(self):
        params = {'limit': invalid_limit}
        response = make_request(
            announcements_url, method='GET', params=params
        )
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(content['Message'])

        print(
            f'Response from {response}, status_code: {response.status_code},\n'
            f'Headers: {response.headers}\n'
            f'Body: {json.loads(response.content)}\n'
        )

    def test_get_all_announcements_request(self):
        response = make_request(announcements_url, method='GET')
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(content['announcements'])
        self.assertGreater(len(content['announcements']), limit)

        print(
            f'Response from {response}, status_code: {response.status_code},\n'
            f'Headers: {response.headers}\n'
            f'Body: {json.loads(response.content)}\n'
        )

    def test_get_particular_announcement_by_title(self):
        response = make_request(
            announcement_url, method='GET', params={'id': test_id}
        )
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['id'], test_id)


if __name__ == '__main__':
    unittest.main()
