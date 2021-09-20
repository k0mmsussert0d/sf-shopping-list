from typing import Optional

from sf_shopping_list.data.clients.dynamodb import user_to_lists_table
from sf_shopping_list.data.db.base_data import BaseDataAccessClass
from sf_shopping_list.data.model.user_to_lists_doc import UserToListsDocModel


class UserToLists(BaseDataAccessClass):

    @staticmethod
    def get(user_sub: str) -> Optional[UserToListsDocModel]:
        res = user_to_lists_table().get_item(
            Key={
                'user_id': user_sub
            },
        )

        if res is None:
            return None

        return UserToListsDocModel.from_db_doc(res['Item'])

    @staticmethod
    def add_list(user_sub: str, list_id: str) -> None:
        user_to_lists_table().update_item(
            Key={
                'user_id': user_sub,
            },
            UpdateExpression='SET #l = list_append(#l, :val)',
            ExpressionAttributeNames={
                '#l': 'lists',
            },
            ExpressionAttributeValues={
                ':val': [list_id]
            },
            ReturnValues='NONE'
        )
