from typing import Dict, Set, List

from mypy_boto3_dynamodb.type_defs import TransactWriteItemTypeDef

from sf_shopping_list.data.db.base_ops import BaseDataOperationsClass
from sf_shopping_list.utils.consts import Consts


class ListsOperations(BaseDataOperationsClass):

    @staticmethod
    def update_guests(list_id: str, user_id: str, guests: Set[str]) -> TransactWriteItemTypeDef:
        return {
            'Update': ListsOperations.merge({
                'Key': {
                    'id': list_id
                },
                'TableName': Consts.LISTS_TABLE,
                'UpdateExpression': 'SET #g = :guests',
                'ExpressionAttributeNames': {
                    '#g': 'guests'
                },
                'ExpressionAttributeValues': {
                    ':guests': guests
                }
            }, ListsOperations.Conditions.is_owner(user_id))}

    @staticmethod
    def update_items(list_id: str, user_id: str, items: List[str]) -> TransactWriteItemTypeDef:
        return {
            'Update': ListsOperations.merge({
                'Key': {
                    'id': list_id
                },
                'TableName': Consts.LISTS_TABLE,
                'UpdateExpression': 'SET #i = :items',
                'ExpressionAttributeNames': {
                    '#i': 'items'
                },
                'ExpressionAttributeValues': {
                    ':items': items
                }
            }, ListsOperations.Conditions.is_owner_or_guest(user_id))}

    class Conditions:

        @staticmethod
        def is_owner(user_id: str) -> Dict:
            return {
                'ConditionExpression': '#u = :userid',
                'ExpressionAttributeNames': {
                    '#u': 'userId'
                },
                'ExpressionAttributeValues': {
                    ':userid': user_id
                }
            }

        @staticmethod
        def is_owner_or_guest(user_id: str) -> Dict:
            return {
                'ConditionExpression': '#u = :userid Or contains(#g, :userid)',
                'ExpressionAttributeNames': {
                    '#u': 'userId',
                    '#g': 'guests'
                },
                'ExpressionAttributeValues': {
                    ':userid': user_id
                }
            }
