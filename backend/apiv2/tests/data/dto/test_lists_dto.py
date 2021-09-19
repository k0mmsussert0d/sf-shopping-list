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


tested_user_id = '1d564127-9f04-47d4-a60c-61e4b8b6cf74'


def test_lists_dto_get_all__if_user_has_no_lists__then_return_empty_list(
        dynamodb_lists_table,
        dynamodb_user_to_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table, user_to_lists_table

    user_to_lists_table().put_item(
        Item={
            'user_id': tested_user_id,
            'lists': [],
        }
    )

    res = ListsDto.get_all(tested_user_id)
    assert res == []


def test_lists_dto_get_all__if_user_owns_the_list__then_return_the_list(
        dynamodb_lists_table,
        dynamodb_user_to_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table, user_to_lists_table

    list0 = sample_data['lists'][0]
    lists_table().put_item(
        Item=list0
    )
    user_to_lists_table().put_item(
        Item={
            'user_id': tested_user_id,
            'lists': [list0['id']]
        }
    )

    res = ListsDto.get_all(tested_user_id)
    assert len(res) == 1
    assert ListMappers.map_dto_to_doc(res[0]) == list0


def test_lists_dto_get_all__if_user_has_guest_access_to_the_list__then_return_the_list(
        dynamodb_lists_table,
        dynamodb_user_to_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table, user_to_lists_table

    list1 = sample_data['lists'][1]
    lists_table().put_item(
        Item=list1
    )
    user_to_lists_table().put_item(
        Item={
            'user_id': tested_user_id,
            'lists': [list1['id']]
        }
    )

    res = ListsDto.get_all(tested_user_id)
    assert len(res) == 1
    assert ListMappers.map_dto_to_doc(res[0]) == list1


def test_lists_dto_get_all__if_user_owns_lists_and_has_guest_access_to_list__then_return_list_of_the_lists_sorted_from_old_to_new(
        dynamodb_lists_table,
        dynamodb_user_to_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table, user_to_lists_table

    list0 = sample_data['lists'][0]
    list1 = sample_data['lists'][1]

    lists_table().put_item(
        Item=list0
    )
    lists_table().put_item(
        Item=list1
    )
    user_to_lists_table().put_item(
        Item={
            'user_id': tested_user_id,
            'lists': [list0['id'], list1['id']]
        }
    )

    res = ListsDto.get_all(tested_user_id)
    assert len(res) == 2
    assert ListMappers.map_dto_to_doc(res[0]) == list1
    assert ListMappers.map_dto_to_doc(res[1]) == list0
