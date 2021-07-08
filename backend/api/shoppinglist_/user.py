import json
import logging
import os
import base64
import boto3
from urllib import parse
from utils import get_attribute


cognito = boto3.client('cognito-idp')


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # TODO: parametrize

def get(event, context):
    logger.debug(event)

    access_token = event['headers']['access-token']
    user_data = cognito.get_user(AccessToken=access_token)

    response = {
        'email': get_attribute(user_data['UserAttributes'], 'email'),
        'username': user_data['Username'],
        'nickname': get_attribute(user_data['UserAttributes'], 'nickname'),
        'avatar': get_attribute(user_data['UserAttributes'], 'picture', '')
    }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'status': 'ok',
            'body': response
        })
    }


def update_avatar(event, context):
    logger.debug(event)

    if event['isBase64Encoded']:
        body = base64.b64decode(event['body']).decode('ascii')
    else:
        body = event['body']

    if not body.isnumeric() or not (1 <= int(body) <= 47):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'status': 'error',
                'reason': 'Invalid avatar identifier'
            })
        }

    app_url = os.environ.get('APP_URL')
    avatar_url = parse.urljoin(app_url, f'/assets/avatars/avatar-{body}.svg')

    cognito.update_user_attributes(
        UserAttributes=[
            {
                'Name': 'picture',
                'Value': avatar_url
            }
        ],
        AccessToken=event['headers']['access-token']
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'status': 'ok',
        })
    }
