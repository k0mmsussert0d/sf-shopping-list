import logging
import os

import boto3
from shortuuid import ShortUUID
import json
from datetime import datetime, timedelta
from utils.decimalencoder import DecimalEncoder
import base64


dynamodb = boto3.resource('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # TODO: parametrize

l_table = dynamodb.Table(os.environ['DYNAMODB_MAIN_TABLE'])
sharing_table = dynamodb.Table(os.environ['DYNAMODB_LISTS_SHARE_TABLE'])


def share_list(event, context):
    list_id = event['pathParameters']['id']
    if event['isBase64Encoded']:
        body = base64.b64decode(event['body'])
    else:
        body = event['body']
    
    try:
        seconds_from_now = int(body)
    except ValueError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'status': 'error',
                'reason': 'Incorrect TTL value'
            })
        }

    if seconds_from_now <= 0:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'status': 'error',
                'reason': 'TTL value must be positive'
            })
        }
    lists = l_table.get_item(
        Key={
            'id': list_id
        }
    )

    if 'Item' not in lists:
        return {
            'statusCode': 404,
            'body': json.dumps({
                'status': 'error',
                'reason': 'List does not exist'
            })
        }

    valid_until = datetime.now() + timedelta(seconds=seconds_from_now)
    item = {
        'id': ShortUUID().random(length=4),
        'list_id': list_id,
        'valid_until': int(valid_until.timestamp())
    }
    sharing_table.put_item(Item=item)

    return {
        'statusCode': 200,
        'body': json.dumps(item, cls=DecimalEncoder)
    }
