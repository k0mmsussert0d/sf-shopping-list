from typing import Optional

from sf_shopping_list.data.db.base_data import BaseDataAccessClass
from sf_shopping_list.data.clients.dynamodb import lists_table
from sf_shopping_list.data.model.list_doc import ListDocModel


class Lists(BaseDataAccessClass):

    @staticmethod
    def get(id: str) -> Optional[ListDocModel]:
        res = lists_table().get_item(
            Key={
                'id': id
            }
        )
        if res['Item']:
            return ListDocModel.from_db_doc(res['Item'])
        return None

    @staticmethod
    def save(lists: ListDocModel) -> None:
        lists_table().put_item(
            Item=lists.dict(),
        )
