from typing import Set

from sf_shopping_list.data.model.base_model import BaseModel


class UserToListsDocModel(BaseModel):
    user_id: str
    lists: Set[str]
