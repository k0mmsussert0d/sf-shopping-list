from typing import List, Set

from sf_shopping_list.data.model.base_model import BaseModel


class ListDocModel(BaseModel):
    id: str
    userId: str
    listName: str
    createdAt: int
    items: List[str]
    guests: Set[str]
