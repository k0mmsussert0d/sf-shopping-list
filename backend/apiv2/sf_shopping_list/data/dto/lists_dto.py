from typing import Optional

from sf_shopping_list.api_models import ListModel
from sf_shopping_list.data.db.lists import Lists
from sf_shopping_list.data.dto.base_dto import BaseDtoClass
from sf_shopping_list.utils.errors import NoAccessError
from sf_shopping_list.utils.mappers.list_mappers import ListMappers


class ListsDto(BaseDtoClass):

    @staticmethod
    def get(id: str, user_sub: str) -> Optional[ListModel]:
        list_doc = Lists.get(id)
        if list_doc is None:
            return None

        if list_doc.userId != user_sub and user_sub not in list_doc.guests:
            raise NoAccessError('User has no access to view this list')

        return ListMappers.map_doc_to_dto(list_doc)
