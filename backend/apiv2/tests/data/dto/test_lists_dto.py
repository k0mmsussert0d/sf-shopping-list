import pytest

from sf_shopping_list.utils.errors import NoAccessError
from sf_shopping_list.utils.mappers.list_mappers import ListMappers


def test_lists_dto_get__if_list_does_not_exist__return_none(dynamodb_lists_table, sample_data):
    from sf_shopping_list.data.dto.lists_dto import ListsDto

    res = ListsDto.get(sample_data['lists'][0]['id'], sample_data['lists'][0]['userId'])
    assert res is None


def test_lists_dto_get__if_list_exists__and_user_is_the_owner__return_the_list(dynamodb_lists_table, sample_data):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list0 = sample_data['lists'][0]

    lists_table().put_item(
        Item=list0,
    )

    res = ListsDto.get(list0['id'], list0['userId'])
    assert ListMappers.map_dto_to_doc(res) == list0


def test_lists_dto_get__if_list_exists__and_user_is_in_guests_list__return_the_list(dynamodb_lists_table, sample_data):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list1 = sample_data['lists'][1]

    lists_table().put_item(
        Item=list1
    )

    res = ListsDto.get(list1['id'], list1['guests'][0])
    assert ListMappers.map_dto_to_doc(res) == list1


def test_lists_dto_get__if_list_exists__and_user_is_not_an_owner__and_user_is_not_in_guests_list__raise_no_access_error(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list1 = sample_data['lists'][1]

    lists_table().put_item(
        Item=list1
    )

    with pytest.raises(NoAccessError):
        ListsDto.get(list1['id'], '1d564127-9f04-47d4-a60c-61e4b8b6cb31')
