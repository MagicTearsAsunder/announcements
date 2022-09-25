import json
from uuid import uuid4

import requests

IS_LOCAL = True

if IS_LOCAL:
    base_url = 'http://127.0.0.1:3000'
else:
    base_url = 'url'

announcement_url = base_url + '/announcement'
announcements_url = base_url + '/announcements'

headers = {
    'Content-Type': 'application/json',
    'x-api-key': 'key',
}

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


if __name__ == '__main__':
    # # Test insert data
    response = make_request(announcement_url, method='POST', data=data)
    print(
        f'Response from {response}, status_code: {response.status_code},\n'
        f'Headers: {response.headers}\n'
        f'Body: {json.loads(response.content)}\n'
    )

    # Test get item by id
    response = make_request(
        announcement_url, params={'id': '4cb779ed'}
    )
    print(
        f'Response from {response}, status_code: {response.status_code},\n'
        f'Headers: {response.headers}\n'
        f'Body: {json.loads(response.content)}\n'
    )

    # Test get all items
    response = make_request(announcements_url)
    print(
        f'Response from {response}, status_code: {response.status_code},\n'
        f'Headers: {response.headers}\n'
        f'Body: {json.loads(response.content)}\n'
    )
