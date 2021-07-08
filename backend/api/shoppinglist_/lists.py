import os
import base64
import json
import time
import logging

from shortuuid import ShortUUID
import boto3

from .utils import DecimalEncoder

dynamodb = boto3.resource('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # TODO: parametrize

l_table = dynamodb.Table(os.environ['DYNAMODB_MAIN_TABLE'])
utl_table = dynamodb.Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE'])


def _add_to_users_lists(user_id, list_id):
    """
    Modifies UserToLists table by appending new list_id to set of lists user has access to.
    If such an entry does not exists in UserToLists table yet, it's being created.

    user_id: user OpenID identifier ('sub' in jwt claims)
    list_id: id of the list to grant access to

    return: {
        user_id: copy of user_id param
        lists: set of lists user has currently access to
    }
    """
    lists = utl_table.update_item(
        Key={
            'user_id': user_id
        },
        UpdateExpression='ADD lists :l',
        ExpressionAttributeValues={
            ':l': {list_id}
        },
        ReturnValues='ALL_NEW'
    )
    return {
        'user_id': user_id,
        'lists': lists
    }


def _delete_from_user_lists(user_id, list_id):
    """
    Modifies UserToLists table by removing list_id from set of lists user has access to.

    user_id: user OpenID identifier ('sub' in jwt claims)
    list_id: id of the list to grant access to

    return: {
        user_id: copy of user_id param
        lists: set of lists user has currently access to
    }
    """
    utl_table.update_item(
        Key={
            'user_id': user_id
        },
        UpdateExpression='DELETE lists :l',
        ExpressionAttributeValues={
            ':l': {list_id}
        }
    )


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

    _add_to_users_lists(user_data['sub'], item_id)

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
            (result['Item']['user_id'] != user_data['sub'] and
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
        'body': json.dumps(res, cls=DecimalEncoder)
    }


def update(event, context):
    logger.debug(event)

    user_data = event['requestContext']['authorizer']['jwt']['claims']
    list_id = event['pathParameters']['id']
    if event['isBase64Encoded']:
        body = base64.b64decode(event['body'])
    else:
        body = event['body']
    data = json.loads(body)
    items = data.get('items')
    list_name = data.get('listName')
    if items is None and list_name is None:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'status': 'error',
                'reason': 'Provide updated items list as a request body'
            })
        }

    result = l_table.get_item(
        Key={
            'id': list_id
        }
    )

    if 'Item' not in result:
        return {
            'statusCode': 404,
            'body': json.dumps({
                'status': 'error',
                'reason': 'List does not exist'
            })
        }

    if result['Item']['user_id'] != user_data['sub'] and user_data['sub'] not in result['Item']['guests']:
        return {
            'statusCode': 401,
            'body': json.dumps({
                'status': 'error',
                'reason': 'You don\'t have access to this list'
            })
        }

    if items is not None:
        l_table.update_item(
            Key={
                'id': list_id
            },
            UpdateExpression='SET #i = :i',
            ExpressionAttributeNames={
                '#i': 'items'
            },
            ExpressionAttributeValues={
                ':i': items
            }
        )
    if list_name is not None:
        l_table.update_item(
            Key={
                'id': list_id
            },
            UpdateExpression='SET list_name = :n',
            ExpressionAttributeValues={
                ':n': list_name
            }
        )

    result = l_table.get_item(
        Key={
            'id': list_id
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps(result['Item'], cls=DecimalEncoder)
    }


def delete(event, context):
    user_data = event['requestContext']['authorizer']['jwt']['claims']
    list_id = event['pathParameters']['id']

    result = l_table.get_item(
        Key={
            'id': list_id
        }
    )

    if 'Item' not in result:
        return {
            'statusCode': 404,
            'body': json.dumps({
                'status': 'error',
                'reason': 'List does not exist'
            })
        }

    if result['Item']['user_id'] != user_data['sub']:
        return {
            'statusCode': 401,
            'body': json.dumps({
                'status': 'error',
                'reason': 'You don\'t have access to this list'
            })
        }

    # TODO: move to "deleted" table instead of deleting for real
    l_table.delete_item(
        Key={
            'id': list_id
        }
    )

    _delete_from_user_lists(user_data['sub'], list_id)
    for guest in result['Item'].get('guests', []):
        _delete_from_user_lists(guest, list_id)

    return {
        'statusCode': 204,
        'body': None
    }
