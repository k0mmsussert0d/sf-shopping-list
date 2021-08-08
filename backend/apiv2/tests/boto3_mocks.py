import os

import boto3
import pytest
from moto import mock_dynamodb2


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'


@pytest.fixture(scope='function')
def dynamodb(aws_credentials):
    with mock_dynamodb2():
        yield boto3.client('dynamodb', region_name='us-east-1')


@pytest.fixture(scope='function')
def dynamodb_lists_table(dynamodb, sls_shared_stack):
    table_resource = sls_shared_stack['resources']['Resources']['ListsDynamoDbTable']
    dynamodb.create_table(
        TableName=os.environ['DYNAMODB_MAIN_TABLE'],
        **table_resource
    )
    yield
    dynamodb.delete_table(
        TableName=os.environ['DYNAMODB_MAIN_TABLE']
    )
