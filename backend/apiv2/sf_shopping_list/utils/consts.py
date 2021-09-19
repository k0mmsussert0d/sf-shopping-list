import os


class Consts:
    LISTS_TABLE = os.environ['DYNAMODB_MAIN_TABLE']
    USER_TO_LISTS_TABLE = os.environ['DYNAMODB_USER_TO_LISTS_TABLE']
