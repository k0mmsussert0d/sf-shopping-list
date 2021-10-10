from typing import Set, Optional

from pydantic import Field

from sf_shopping_list.data.model.base_model import BaseModel


class UserToListsDocModel(BaseModel):
    user_id: str
    lists: Optional[Set[str]] = Field(default_factory=lambda: set())
