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

l_table = dynamodb.Table(os.environ['DYNAMODB_MAIN_TABLE'])
utl_table = dynamodb.Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE'])

def add_or_update(user_id, list_id):
    result = utl_table.get_item(
        Key={
            'user_id': user_id
        }
    )

    if not 'Item' in result:
        item = {
            'user_id': user_id,
            'lists': [list_id]
        }
        utl_table.put_item(
            Item=item
        )

        return item
    else:
        lists = result['Item']['lists']
        lists.append(list_id)
        utl_table.update_item(
            Key={
                'user_id': user_id
            },
            UpdateExpression="set lists = :l",
            ExpressionAttributeValues={
                ':l': lists
            },
        )

        return {
            'user_id': user_id,
            'lists': lists
        }


def create(event, context):
    logger.debug(event)

    if event['isBase64Encoded']:
        body = base64.b64decode(event['body'])
    else:
        body = event['body']
    data = json.loads(body)

    user_data = event['requestContext']['authorizer']['jwt']['claims']

    if 'name' not in data:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'status': 'error',
                'reason': '"name" attribute has not been provided'
            })
        }
    items = data.get('items', [])
    guests = data.get('guests', [])

    item_id = ShortUUID().random(length=6)
    timestamp = int(time.time())

    item = {
        'id': item_id,
        'user_id': user_data['sub'],
        'list_name': data['name'],
        'created_at': timestamp,
        'items': items,
        'guests': guests
    }

    l_table.put_item(Item=item)

    add_or_update(user_data['sub'], item_id)

    return {
        'statusCode': 200,
        'body': json.dumps(item)
    }

def get(event, context):
    logger.debug(event)

    user_data = event['requestContext']['authorizer']['jwt']['claims']
    result = l_table.get_item(
        Key={
            'id': event['pathParameters']['id']
        }
    )
    logger.debug(result)

    if 'Item' not in result or \
        (result['Item']['user_id'] != user_data['sub'] and \
         not user_data['sub'] in result['Item']['guests']):
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
    user_lists = utl_table.get_item(
        Key={
            'user_id': user_data['sub']
        }
    )

    if 'Item' not in user_lists:
        return {
            'statusCode': 200,
            'body': []
        }

    res = []
    for user_list in user_lists['Item']['lists']:
        lists = l_table.get_item(
            Key={
                'id': user_list
            }
        )
        if 'Item' not in lists:
            logging.error(f'User has access to {user_list} list but it can\'t be found')
        else:
            res.append(lists['Item'])

    logger.debug(res)

    return {
        'statusCode': 200,
        'body': json.dumps(res,  cls=DecimalEncoder)
    }
