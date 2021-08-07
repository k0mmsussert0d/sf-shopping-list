import boto3
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table

from sf_shopping_list.utils.consts import Consts


def dynamodb() -> DynamoDBServiceResource:
    return boto3.resource('dynamodb')


def lists_table() -> Table:
    return dynamodb().Table(Consts.LISTS_TABLE)
