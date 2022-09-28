from validator import validate
from serializer import DecimalEncoder

import os
import json
import logging
from uuid import uuid4
from datetime import date

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DBNAME = os.environ['DBNAME']
REGION = os.environ['REGION']
QLIMIT = int(os.environ['QLIMIT'])

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(DBNAME)

announcement_path = '/announcement'
announcements_path = '/announcements'


def build_response(status_code, body=None):
    response = {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
        }
    }

    if body:
        response['body'] = json.dumps(body, cls=DecimalEncoder)

    return response


def get_announcement(params=None, body=None):
    logging.info(
        f'In get_announcement: params:{params}, body: {body}'
    )

    if not params or not params.get('id'):
        return build_response(400, {'Message': 'Requires param "id"'})

    pk = params['id']
    response = table.get_item(Key={'id': pk})
    if 'Item' in response:
        return build_response(200, response['Item'])
    else:
        return build_response(400, {'Message': f'id: {pk} not found'})


def list_announcements(params=None, body=None):
    logging.info(
        f'In list_announcements: params:{params}, body: {body}'
    )

    params = params or {}

    if 'limit' in params:
        try:
            limit = int(params['limit'])
        except ValueError:
            return build_response(
                400,
                {'Message': f'limit: {params["limit"]} '
                 'is not a valid value'}
            )
    else:
        limit = QLIMIT

    response = table.scan(Limit=limit)
    result = response['Items']
    limit -= len(response['Items'])

    while 'LastEvaluatedKey' in response and limit:
        response = table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey'], Limit=limit
        )
        limit -= len(response['Items'])
        result.extend(response['Items'])

    return build_response(200, {'announcements': result})


def post_announcement(params=None, body=None):
    body = json.loads(body)
    logging.info(
        f'In post_announcement: params:{params}, body: {body}, '
        f'type body: {type(body)}'
    )

    if validate(body):
        body.update({
            'id': str(uuid4())[:8],
            'date': str(date.today()),
        })
        table.put_item(Item=body)
        body = {
            'Message': 'Success',
            'Item': body
        }
        return build_response(200, body)
    else:
        return build_response(406, 'Not Acceptable')


def lambda_handler(event, context):
    logging.info(f'Event: {event}')
    logging.info(f'Context: {context}')

    http_method = event['httpMethod']
    path = event['path']

    logging.info(f'path: {path}')
    logging.info(f'http_method: {http_method}')

    path_method_dict = {
        ('GET', announcement_path): get_announcement,
        ('GET', announcements_path): list_announcements,
        ('POST', announcement_path): post_announcement,
    }

    callback = path_method_dict.get((http_method, path), None)

    params = event.get('queryStringParameters')
    body = event.get('body')

    if callback:
        response = callback(params=params, body=body)
    else:
        response = build_response(404, 'Not Found')

    return response
