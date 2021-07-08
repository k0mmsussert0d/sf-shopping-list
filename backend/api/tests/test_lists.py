import os

import json
import pytest
import boto3

from tests.setup import dynamodb, aws_credentials, environment
import uuid


@pytest.fixture(scope='function')
def list_details():
    return {
        'user_id': '613a7aa2-3dda-444d-baca-8711455f1bfa',
        'list_name': 'test name',
        'items': ['item1', 'item2', 'item3'],
    }


@pytest.fixture(scope='function')
def list_expected_details():
    return {
        'id': 'FOOBAR',
        'created_at': 1616240181,
        'guests': []
    }


@pytest.fixture
def populate_default_list_item(list_details, list_expected_details):
    main_table = boto3.resource('dynamodb').Table(os.environ.get('DYNAMODB_MAIN_TABLE'))
    user_to_lists_table = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE'])

    target_list_details = {
        **list_details,
        **list_expected_details
    }

    main_table.put_item(
        Item=target_list_details
    )

    user_to_lists_table.put_item(
        Item={
            'user_id': target_list_details.get('user_id'),
            'lists': {target_list_details.get('id')},
        }
    )

    for guest in target_list_details.get('guests', []):
        user_to_lists_table.put_item(
            Item={
                'user_id': guest,
                'lists': {target_list_details.get('id')},
            }
        )

    yield target_list_details

    main_table.delete_item(
        Key={
            'id': target_list_details.get('id')
        }
    )

    for user in target_list_details.get('guests', []) + [target_list_details.get('user_id')]:
        user_to_lists_table.update_item(
            Key={
                'user_id': user
            },
            UpdateExpression='DELETE lists :l',
            ExpressionAttributeValues={
                ':l': {target_list_details.get('id')}
            }
        )


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
        assert result_item['Item'][detail_name] == detail_value, \
            f'Item detail does not have expected value: {detail_value}, actual: {result_item["Item"][detail_name]}'
    for detail_name in list_expected_details:
        assert detail_name in result_item['Item'], f'Item does not have required detail: {detail_name}'
        assert result_item['Item'][
                   detail_name] is not None, f'Item does not have required detail set to value: {detail_name}'

    user_to_table_item = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE']).get_item(
        Key={
            'user_id': list_details.get('user_id')
        }
    )
    assert 'Item' in user_to_table_item, 'Item insertion did not update user_to_lists table'
    assert result_item['Item']['id'] in user_to_table_item['Item'][
        'lists'], 'New list has not been added to user\'s list of lists'


def test_delete_list_not_owned_list_is_not_deleted(dynamodb, list_details, list_expected_details):
    from shoppinglist.lists import delete

    target_list_details = {**list_details, **list_expected_details, 'user_id': 'other_user_guid'}
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


def test_delete_list_owned_list_is_deleted(dynamodb, list_details, list_expected_details):
    from shoppinglist.lists import delete

    list_details = {
        **list_details,
        **list_expected_details
    }

    guest_user_uuid = str(uuid.uuid4())
    list_details['guests'].append(guest_user_uuid)

    boto3.resource('dynamodb').Table(os.environ['DYNAMODB_MAIN_TABLE']).put_item(
        Item=list_details
    )
    boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE']).put_item(
        Item={
            'user_id': list_details.get('user_id'),
            'lists': {list_details.get('id')},
        }
    )
    boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE']).put_item(
        Item={
            'user_id': guest_user_uuid,
            'lists': {list_details.get('id')},
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
    owner_access_list = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE']).get_item(
        Key={
            'user_id': list_details.get('user_id')
        }
    )
    guest_access_list = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE']).get_item(
        Key={
            'user_id': guest_user_uuid
        }
    )

    assert 'Item' not in list_item, 'List item has not been removed'
    assert list_details['id'] not in owner_access_list['Item'][
        'lists'], 'List of lists owner has access to has not been updated after list deletion'
    assert list_details['id'] not in guest_access_list['Item'][
        'lists'], 'List of lists guest has access to has not been updated after list deletion'


def test_get_list_returns_list_if_list_is_owner(dynamodb, list_details, list_expected_details):
    from shoppinglist.lists import get

    list_details = {
        **list_details,
        **list_expected_details
    }

    boto3.resource('dynamodb').Table(os.environ['DYNAMODB_MAIN_TABLE']).put_item(
        Item=list_details
    )
    boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE']).put_item(
        Item={
            'user_id': list_details.get('user_id'),
            'lists': {list_details.get('id')},
        }
    )

    result = get({
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
        }}, {})

    assert result['statusCode'] == 200 and json.loads(result['body']) == list_details, \
        'List has not been correctly returned, even though user is the owner'


def test_get_list_returns_list_if_user_on_guests_list(dynamodb, list_details, list_expected_details):
    from shoppinglist.lists import get

    user_id = list_details['user_id']
    other_user_id = str(uuid.uuid4())
    list_details = {
        **list_details,
        **list_expected_details,
        'user_id': other_user_id,
        'guests': {user_id}
    }

    boto3.resource('dynamodb').Table(os.environ['DYNAMODB_MAIN_TABLE']).put_item(
        Item=list_details
    )
    boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE']).put_item(
        Item={
            'user_id': other_user_id,
            'lists': {list_details.get('id')},
        }
    )
    boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE']).put_item(
        Item={
            'user_id': user_id,
            'lists': {list_details.get('id')},
        }
    )

    result = get({
        'pathParameters': {
            'id': list_details.get('id')
        },
        'requestContext': {
            'authorizer': {
                'jwt': {
                    'claims': {
                        'sub': user_id
                    }
                }
            }
        }
    }, {})

    expected = {**list_details, 'guests': list(list_details['guests'])}
    assert result['statusCode'] == 200 and json.loads(result['body']) == expected, \
        f'List has not been correctly returned, even though user is on the guests list\n' \
        f'{json.loads(result["body"])} != {expected}'


def test_get_list_returns_not_found_in_user_is_not_an_owner_or_guest(dynamodb, list_details, list_expected_details):
    from shoppinglist.lists import get

    user_id = list_details['user_id']
    other_user_id = str(uuid.uuid4())
    list_details = {
        **list_details,
        **list_expected_details,
        'user_id': other_user_id,
    }

    boto3.resource('dynamodb').Table(os.environ['DYNAMODB_MAIN_TABLE']).put_item(
        Item=list_details
    )
    boto3.resource('dynamodb').Table(os.environ['DYNAMODB_USER_TO_LISTS_TABLE']).put_item(
        Item={
            'user_id': other_user_id,
            'lists': {list_details.get('id')},
        }
    )

    result = get({
        'pathParameters': {
            'id': list_details.get('id')
        },
        'requestContext': {
            'authorizer': {
                'jwt': {
                    'claims': {
                        'sub': user_id
                    }
                }
            }
        }
    }, {})

    assert result['statusCode'] == 404, f'Access to the list has not been correctly denied'


def test_get_all_lists_return_lists_user_has_access_to():
    pass


def test_update_list_ok_if_user_is_owner():
    pass


def test_update_list_ok_if_user_is_guest():
    pass


def test_update_list_not_found_if_user_is_not_an_owner_or_guest():
    pass
