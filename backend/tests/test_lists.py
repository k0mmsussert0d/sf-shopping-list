import os

import json
import pytest
import boto3

from tests.setup import dynamodb, aws_credentials, environment
import time


@pytest.fixture(scope='function')
def list_details():
    return {
        'user_id': '613a7aa2-3dda-444d-baca-8711455f1bfa',
        'list_name': 'test name',
        'items': ['item1', 'item2', 'item3'],
    }

@pytest.fixture(scope='function')
def list_expected_details(list_details):
    return ['id', 'created_at', 'guests']

def test_create_list_new_list_is_added(dynamodb, environment, list_details, list_expected_details):
    from shoppinglist.lists import create

    res = create({
        'isBase64Encoded': False,
        'body': json.dumps({
            'name': list_details.get('list_name'),
            'items': list_details.get('items')
        }),
        'requestContext': {
            'authorizer': {
                'jwt': {
                    'claims': {
                        'sub': list_details.get('user_id')
                    }
                }
            }
        }
    }, None)
    res_body = json.loads(res['body'])

    result_item = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_MAIN_TABLE']).get_item(
        Key={
            'id': res_body['id']
        }
    )
    assert 'Item' in result_item, 'Item has not been created in the database'
    for detail_name, detail_value in list_details.items():
        assert detail_name in result_item['Item'], f'Item does not have required detail: {detail_name}'
        assert result_item['Item'][detail_name] == detail_value,\
        f'Item detail does not have expected value: {detail_value}, actual: {result_item["Item"][detail_name]}'
    for detail_name in list_expected_details:
        assert detail_name in result_item['Item'], f'Item does not have required detail: {detail_name}'
        assert result_item['Item'][detail_name] is not None, f'Item does not have required detail set to value: {detail_name}'

    user_to_table_item = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE']).get_item(
        Key={
            'user_id': list_details.get('user_id')
        }
    )
    assert 'Item' in user_to_table_item, 'Item insertion did not update user_to_lists table'
    assert result_item['Item']['id'] in user_to_table_item['Item']['lists'], 'New list has not been added to user\'s list of lists'

def test_delete_list_not_owned_list_is_not_deleted(dynamodb, list_details):
    from shoppinglist.lists import delete

    target_list_details = {
        **list_details,
        'id': 'FOOBAR',
        'created_at': int(time.time()),
        'guests': [],
    }
    target_list_details['user_id'] = 'other_user_guid'
    boto3.resource('dynamodb').Table(os.environ['DYNAMODB_MAIN_TABLE']).put_item(
        Item=target_list_details
    )

    delete({
        'pathParameters': {
            'id': target_list_details.get('id')
        },
        'requestContext': {
            'authorizer': {
                'jwt': {
                    'claims': {
                        'sub': list_details.get('user_id')
                    }
                }
            }
        }
    }, {})
    result_item = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_MAIN_TABLE']).get_item(
        Key={
            'id': target_list_details.get('id')
        }
    )
    assert 'Item' in result_item, 'List has been delete, even though it shouldn\'t be'


def test_delete_list_owned_list_is_deleted(dynamodb, list_details):
    from shoppinglist.lists import delete

    list_details = {
        **list_details,
        'id': 'FOOBAR',
        'created_at': int(time.time()),
        'guests': [],
    }

    boto3.resource('dynamodb').Table(os.environ['DYNAMODB_MAIN_TABLE']).put_item(
        Item=list_details
    )
    boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE']).put_item(
        Item={
            'user_id': list_details.get('user_id'),
            'lists': ['FOOBAR'],
        }
    )

    delete({
        'pathParameters': {
            'id': list_details.get('id')
        },
        'requestContext': {
            'authorizer': {
                'jwt': {
                    'claims': {
                        'sub': list_details.get('user_id')
                    }
                }
            }
        }
    }, {})
    list_item = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_MAIN_TABLE']).get_item(
        Key={
            'id': list_details.get('id')
        }
    )
    access_item = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE']).get_item(
        Key={
            'user_id': list_details.get('user_id')
        }
    )

    assert 'Item' not in list_item, 'List item has not been removed'
    assert list_details['id'] not in access_item['Item']['lists'], 'List of lists user has access to has not been updated after list deletion'
