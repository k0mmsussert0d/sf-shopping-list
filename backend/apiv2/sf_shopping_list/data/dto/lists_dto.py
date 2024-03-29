from datetime import datetime
from typing import Optional, List

from shortuuid import ShortUUID

from sf_shopping_list.api_models import ListModel, NewList
from sf_shopping_list.data.db.lists import Lists
from sf_shopping_list.data.db.user_to_lists import UserToLists
from sf_shopping_list.data.dto.base_dto import BaseDtoClass
from sf_shopping_list.utils.errors import NoAccessError
from sf_shopping_list.utils.mappers.list_mappers import ListMappers


class ListsDto(BaseDtoClass):

    @staticmethod
    def get(id: str, user_sub: str) -> Optional[ListModel]:
        list_doc = Lists.get(id)
        if list_doc is None:
            return None

        if not ListsDto._user_has_access_to_list(list_doc, user_sub):
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
        UserToLists.add_list(user_sub, list_dto.id)
        for guest_id in new_list_dto.guests:
            UserToLists.add_list(guest_id, list_dto.id)
        return list_dto

    @staticmethod
    def update(id: str, new_list: ListModel, user_sub: str) -> Optional[ListModel]:
        curr_list = ListsDto.get(id, user_sub)
        if not curr_list:
            return None
        else:
            if user_sub in curr_list.guests:  # is guest, cannot modify listName and guests
                if curr_list.listName != new_list.listName or curr_list.guests != new_list.guests:
                    raise NoAccessError('Guest is not allowed to modify those attributes')

        # rewrite immutable properties from existing item
        new_list.id = id
        new_list.createdAt = curr_list.createdAt
        new_list.userId = curr_list.userId

        # update access entries for users denied access
        for non_guest in (set(curr_list.guests) - set(new_list.guests)):
            UserToLists.remove_list(non_guest, id)

        # update access entries for users given access
        for guest in new_list.guests:
            UserToLists.add_list(guest, id)

        Lists.save(ListMappers.map_dto_to_doc(new_list))
        return new_list

    @staticmethod
    def add_item(id: str, new_item: str, user_sub: str) -> List[str]:
        return Lists.append_items(id, [new_item], user_sub)

    @staticmethod
    def update_item(id: str, item_idx: int, new_item: str, user_sub: str) -> List[str]:
        return Lists.update_item(id, item_idx, new_item, user_sub)

    @staticmethod
    def remove_item(id: str, item_idx: int, user_sub: str) -> List[str]:
        return Lists.remove_items(id, [item_idx], user_sub)

    @staticmethod
    def update_items(id: str, items: List[str], user_sub: str) -> List[str]:
        return Lists.update_items(id, items, user_sub)

    @staticmethod
    def _user_has_access_to_list(list_doc, user_sub):
        return list_doc.userId == user_sub or user_sub in list_doc.guests

