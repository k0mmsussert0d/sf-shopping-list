import os
import base64
import json
import time
import logging

from shortuuid import ShortUUID
import boto3
from boto3.dynamodb.conditions import Attr

from utils import DecimalEncoder

dynamodb = boto3.resource('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # TODO: parametrize

def create(event, context):
    logger.debug(event)
    logger.debug(context)

    if event['isBase64Encoded']:
        body = base64.b64decode(event['body'])
    else:
        body = event['body']
    data = json.loads(body)

    user_data = event['requestContext']['authorizer']['jwt']['claims']

    if 'name' not in data:
        logging.error('No list name provided')
        raise Exception('Could not create list')
    items = data.get('items', [])
    guests = data.get('guests', [])

    item_id = ShortUUID().random(length=6)
    timestamp = int(time.time())

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    item = {
        'id': item_id,
        'user_id': user_data['sub'],
        'list_name': data['name'],
        'created_at': timestamp,
        'items': items,
        'guests': guests
    }

    table.put_item(Item=item)

    return {
        'statusCode': 200,
        'body': json.dumps(item)
    }

def get(event, context):
    logger.debug(event)

    user_data = event['requestContext']['authorizer']['jwt']['claims']

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    result = table.get_item(
        Key={
            'id': event['pathParameters']['id']
        }
    )
    logger.debug(result)

    if result['Item']['user_id'] != user_data['sub'] and not user_data['sub'] in result['Item']['guests']:
        return {
            'statusCode': 404,
            'body': 'You don\'t have access to this list or it doesn\'t exist'
        }

    return {
        'statusCode': 200,
        'body': json.dumps(result['Item'], cls=DecimalEncoder)
    }

def get_all(event, context):
    logger.debug(event)

    user_data = event['requestContext']['authorizer']['jwt']['claims']

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    results = table.scan(
        FilterExpression=Attr('guests').contains(user_data['sub'])
    )
    logger.debug(results)

    return {
        'statusCode': 200,
        'body': json.dumps(results['Items'], cls=DecimalEncoder)
    }
