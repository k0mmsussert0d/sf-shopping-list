from typing import Optional, List

from sf_shopping_list.data.clients.dynamodb import lists_table, user_to_lists_table
from sf_shopping_list.data.db.base_data import BaseDataAccessClass
from sf_shopping_list.data.db.user_to_lists import UserToLists
from sf_shopping_list.data.model.list_doc import ListDocModel


class Lists(BaseDataAccessClass):

    @staticmethod
    def get(id: str) -> Optional[ListDocModel]:
        res = lists_table().get_item(
            Key={
                'id': id
            }
        )
        if 'Item' in res:
            return ListDocModel.from_db_doc(res['Item'])
        return None

    @staticmethod
    def get_all(user_sub: str) -> List[ListDocModel]:
        res = user_to_lists_table().get_item(
            Key={
                'user_id': user_sub
            }
        )

        return sorted([Lists.get(id) for id in res['Item']['lists']], key=lambda l: l.createdAt, reverse=True)

    @staticmethod
    def save(lists: ListDocModel) -> None:
        lists_table().put_item(
            Item=lists.dict(),
        )

        UserToLists.add_list(lists.userId, lists.id)
        for guest_id in lists.guests:
            UserToLists.add_list(guest_id, lists.id)

    @staticmethod
    def append_items(id: str, items: List[str], user_id: str) -> List[str]:
        with Lists._handle_conditional_check_fail():
            res = lists_table().update_item(
                Key={
                    'id': id
                },
                UpdateExpression='SET #i = list_append(#i, :vals)',
                ConditionExpression='#u = :userid Or contains(#g, :userid)',
                ExpressionAttributeNames={
                    '#i': 'items',
                    '#u': 'userId',
                    '#g': 'guests'
                },
                ExpressionAttributeValues={
                    ':vals': items,
                    ':userid': user_id
                },
                ReturnValues='UPDATED_NEW'
            )

            if res:
                return list(res['Attributes']['items'])

    @staticmethod
    def update_item(id: str, idx: int, new_item: str, user_id: str) -> List[str]:
        with Lists._handle_conditional_check_fail():
            res = lists_table().update_item(
                Key={
                    'id': id
                },
                UpdateExpression=f'SET #i[{str(idx)}] = :val',
                ConditionExpression='#u = :userid Or contains(#g, :userid)',
                ExpressionAttributeNames={
                    '#i': 'items',
                    '#u': 'userId',
                    '#g': 'guests',
                },
                ExpressionAttributeValues={
                    ':userid': user_id,
                    ':val': new_item
                },
                ReturnValues='UPDATED_NEW'
            )

            if res:
                return list(res['Attributes']['items'])

    @staticmethod
    def remove_items(id: str, indices: List[int], user_id: str) -> List[str]:
        with Lists._handle_conditional_check_fail():
            res = lists_table().update_item(
                Key={
                    'id': id
                },
                UpdateExpression='REMOVE ' + ' '.join([f'#i[{i}]' for i in indices]),
                ConditionExpression='#u = :userid Or contains(#g, :userid)',
                ExpressionAttributeNames={
                    '#i': 'items',
                    '#u': 'userId',
                    '#g': 'guests'
                },
                ExpressionAttributeValues={
                    ':userid': user_id
                },
                ReturnValues='UPDATED_NEW'
            )

            if res:
                return list(res['Attributes']['items'])

    @staticmethod
    def update_items(id: str, items: List[str], user_id: str) -> List[str]:
        with Lists._handle_conditional_check_fail():
            res = lists_table().update_item(
                Key={
                    'id': id
                },
                UpdateExpression='SET #i = :i',
                ConditionExpression='#u = :userid Or contains(#g, :userid)',
                ExpressionAttributeNames={
                    '#i': 'items',
                    '#u': 'userId',
                    '#g': 'guests'
                },
                ExpressionAttributeValues={
                    ':i': items,
                    ':userid': user_id
                },
                ReturnValues='UPDATED_NEW'
            )

            if res:
                return list(res['Attributes']['items'])
