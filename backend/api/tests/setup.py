import os
from shutil import which

import pytest
import boto3
from moto import mock_dynamodb2
import yaml
from yaml.scanner import ScannerError
import subprocess


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'


@pytest.fixture
def environment():
    os.environ['DYNAMODB_MAIN_TABLE'] = 'sf-shopping-list-dev-main-table'
    os.environ['DYNAMODB_USER_TO_LISTS_TABLE'] = 'sf-shopping-list-dev-user-to-lists-table'
    os.environ['DYNAMODB_LISTS_SHARE_TABLE'] = 'sf-shopping-list-dev-lists-share-table'


def _load_file():
    cwd = os.path.dirname(os.path.realpath(__file__))
    locations = [
        cwd + '/../serverless.yml',
        cwd + '/serverless.yml',
        'serverless.yml',
    ]
    serverless_path = None
    for location in locations:
        if os.path.isfile(location):
            serverless_path = os.path.dirname(location)
            break
    
    if not serverless_path:
        raise Exception("No serverless.yml file found!")

    if not which("sls"):
        raise Exception("No sls executable found!")

    env = os.environ.copy()
    env["SLS_DEPRECATION_DISABLE"] = "*"
    env["SLS_WARNING_DISABLE"] = "*"
    result = subprocess.run(["sls", "print"], stdout=subprocess.PIPE, env=env, cwd=serverless_path)
    serverless_content = result.stdout.decode("utf-8").replace(
        'Serverless: Running "serverless" installed locally (in service node_modules)\n',
        "",
    )

    try:
        return yaml.safe_load(serverless_content)
    except ScannerError as e:
        pytest.fail(
            f"serverless.yml is wrongly formatted, pytest-serverless is unable to load it: {e}"
        )


def _get_property(properties, property_names):
    return {name: properties[name] for name in property_names if name in properties}


def _prepare_dynamodb_table(resources):
    from moto import mock_dynamodb2
    dynamodb = mock_dynamodb2()

    def before():
        dynamodb.start()

        for resource_definition in resources:
            boto3.resource('dynamodb').create_table(
                **_get_property(
                    resource_definition["Properties"],
                    (
                        "TableName",
                        "AttributeDefinitions",
                        "KeySchema",
                        "LocalSecondaryIndexes",
                        "GlobalSecondaryIndexes",
                        "BillingMode",
                        "ProvisionedThroughput",
                        "StreamSpecification",
                        "SSESpecification",
                        "Tags",
                    ),
                )
            )
    
    def after():
        for resource_definition in resources:
            boto3.client('dynamodb').delete_table(
                TableName=resource_definition['Properties']['TableName']
            )

        dynamodb.stop()

    return before, after


@pytest.fixture(scope='function')
def dynamodb(aws_credentials, environment):
    sls = _load_file()
    tables = list(
        filter(
            lambda x: x.get('Type') == 'AWS::DynamoDB::Table',
            sls.get('resources', {}).get('Resources', {}).values()
            )
        )
    before, after = _prepare_dynamodb_table(tables)

    before()

    yield
    
    after()
