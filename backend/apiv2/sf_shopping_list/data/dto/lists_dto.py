from datetime import datetime
from typing import Optional, List

from shortuuid import ShortUUID

from sf_shopping_list.api_models import ListModel, NewList
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

    @staticmethod
    def get_all(user_sub: str) -> List[ListModel]:
        return [ListMappers.map_doc_to_dto(d) for d in Lists.get_all(user_sub)]

    @staticmethod
    def create(new_list_dto: NewList, user_sub: str) -> ListModel:
        list_dto = ListModel(
            id=ShortUUID.random(length=6),
            userId=user_sub,
            listName=new_list_dto.name,
            createdAt=datetime.utcnow(),
            items=new_list_dto.items,
            guests=new_list_dto.guests,
        )
        Lists.save(ListMappers.map_dto_to_doc(list_dto))
        return list_dto

