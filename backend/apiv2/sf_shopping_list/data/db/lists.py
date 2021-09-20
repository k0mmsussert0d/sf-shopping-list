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
        # TODO: execute in transaction
        lists_table().put_item(
            Item=lists.dict(),
        )

        UserToLists.add_list(lists.userId, lists.id)
        for guest_id in lists.guests:
            UserToLists.add_list(guest_id, lists.id)
