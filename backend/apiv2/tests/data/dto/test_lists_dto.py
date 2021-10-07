import copy
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from sf_shopping_list.api_models import NewList
from sf_shopping_list.data.model.list_doc import ListDocModel
from sf_shopping_list.utils.errors import NoAccessError, NotFoundError
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
    assert ListMappers.map_dto_to_doc(res) == ListDocModel.from_db_doc(list0)


def test_lists_dto_get__if_list_exists__and_user_is_in_guests_list__return_the_list(dynamodb_lists_table, sample_data):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list1 = sample_data['lists'][1]

    lists_table().put_item(
        Item=list1
    )

    res = ListsDto.get(list1['id'], list1['guests'][0])
    assert ListMappers.map_dto_to_doc(res) == ListDocModel.from_db_doc(list1)


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
    from sf_shopping_list.data.clients.dynamodb import user_to_lists_table

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
    assert ListMappers.map_dto_to_doc(res[0]) == ListDocModel.from_db_doc(list0)


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
    assert ListMappers.map_dto_to_doc(res[0]) == ListDocModel.from_db_doc(list1)


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
    assert ListMappers.map_dto_to_doc(res[0]) == ListDocModel.from_db_doc(list1)
    assert ListMappers.map_dto_to_doc(res[1]) == ListDocModel.from_db_doc(list0)


added_time = datetime.utcfromtimestamp(1632167964.0)
added_id = 'ABCdef'


@patch('shortuuid.ShortUUID.random', MagicMock(return_value=added_id))
def test_lists_dto_add__when_new_list_is_added__then_update_dynamodb__and_return_saved_object(
        dynamodb_lists_table,
        dynamodb_user_to_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table, user_to_lists_table

    guest_user_id = 'guest1_id'

    # initialize user_to_lists entries for owner and guest
    user_to_lists_table().put_item(
        Item={
            'user_id': tested_user_id,
            'lists': [],
        }
    )
    user_to_lists_table().put_item(
        Item={
            'user_id': guest_user_id,
            'lists': []
        }
    )

    # add new list
    new_list = NewList(
        name='new sample list',
        items=[
            'item0',
            'item1',
            'item2',
        ],
        guests=[guest_user_id]
    )

    with patch('sf_shopping_list.data.dto.lists_dto.datetime', spec=datetime) as mock_date:
        mock_date.utcnow.return_value = added_time
        res = ListsDto.create(new_list, tested_user_id)

    # assert returned object has all fields filled correctly
    assert res.id == added_id
    assert res.userId == tested_user_id
    assert res.createdAt == added_time
    assert res.guests == new_list.guests
    assert res.items == new_list.items
    assert res.listName == new_list.name

    # assert returned object has been persisted
    saved_list = lists_table().get_item(
        Key={
            'id': added_id
        }
    )
    assert saved_list['Item'] is not None
    assert ListMappers.map_doc_to_dto(ListDocModel.from_db_doc(saved_list['Item'])) == res

    # assert owner user_to_lists entry has been updated with new list
    owner_lists = user_to_lists_table().get_item(
        Key={
            'user_id': tested_user_id
        }
    )
    assert owner_lists['Item'] is not None
    assert added_id in owner_lists['Item']['lists']

    # assert guest user_to_lists entry has been updated with new list
    guest_lists = user_to_lists_table().get_item(
        Key={
            'user_id': guest_user_id
        }
    )
    assert guest_lists['Item'] is not None
    assert added_id in owner_lists['Item']['lists']


def test_lists_dto_add_item__when_list_does_not_exist__raise_not_found_error(
        dynamodb_lists_table
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto

    with pytest.raises(NotFoundError):
        ListsDto.add_item('abcdef', 'new item', tested_user_id)


def test_lists_dto_add_item__when_user_has_no_access__raise_unauthorized_error(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list0 = copy.deepcopy(sample_data['lists'][0])
    list0['userId'] = 'other_sub_id'

    lists_table().put_item(
        Item=list0
    )

    with pytest.raises(NotFoundError):
        ListsDto.add_item(list0['id'], 'new item', tested_user_id)


def test_lists_dto_add_item__when_user_is_owner__update_the_list(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list0 = sample_data['lists'][0]
    lists_table().put_item(
        Item=list0
    )
    list_id = list0['id']

    new_item = 'new item'
    res = ListsDto.add_item(list_id, new_item, tested_user_id)

    res_saved = lists_table().get_item(
        Key={
            'id': list_id
        }
    )

    assert new_item in res
    assert new_item in res_saved['Item']['items']


def test_lists_dto_add_item__when_user_is_guest__update_the_list(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list1 = sample_data['lists'][1]
    lists_table().put_item(
        Item=list1
    )
    list_id = list1['id']

    new_item = 'new item'
    res = ListsDto.add_item(list_id, new_item, tested_user_id)

    res_saved = lists_table().get_item(
        Key={
            'id': list_id
        }
    )

    assert new_item in res
    assert new_item in res_saved['Item']['items']


def test_lists_dto_remove_item__when_list_does_not_exist__raise_not_found_error(
        dynamodb_lists_table
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto

    with pytest.raises(NotFoundError):
        ListsDto.remove_item('abcdef', 0, tested_user_id)


def test_lists_dto_remove_item__when_user_has_no_access__raise_not_found_error(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list0 = copy.deepcopy(sample_data['lists'][0])
    list0['userId'] = 'other_sub_id'

    lists_table().put_item(
        Item=list0
    )

    with pytest.raises(NotFoundError):
        ListsDto.remove_item(list0['id'], 0, tested_user_id)


def test_lists_dto_remove_item__when_user_is_owner__update_the_list(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list0 = sample_data['lists'][0]
    lists_table().put_item(
        Item=list0
    )
    list_id = list0['id']
    item = list0['items'][0]
    res = ListsDto.remove_item(list_id, 0, tested_user_id)

    res_saved = lists_table().get_item(
        Key={
            'id': list_id
        }
    )

    assert item not in res
    assert item not in res_saved['Item']['items']


def test_lists_dto_remove_item__when_user_is_guest__update_the_list(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list1 = sample_data['lists'][1]
    lists_table().put_item(
        Item=list1
    )
    list_id = list1['id']
    item = list1['items'][0]
    res = ListsDto.remove_item(list_id, 0, tested_user_id)

    res_saved = lists_table().get_item(
        Key={
            'id': list_id
        }
    )

    assert item not in res
    assert item not in res_saved['Item']['items']


def test_lists_dto_update_items__when_list_does_not_exist__raise_not_found_error(
        dynamodb_lists_table
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto

    with pytest.raises(NotFoundError):
        ListsDto.update_items('abcdef', ['item0', 'item1'], tested_user_id)


def test_lists_dto_update_items__when_user_has_no_access__raise_not_found_error(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list0 = copy.deepcopy(sample_data['lists'][0])
    list0['userId'] = 'other_user_id'

    lists_table().put_item(
        Item=list0
    )

    with pytest.raises(NotFoundError):
        ListsDto.update_items(list0['id'], ['item0', 'item1'], tested_user_id)


def test_lists_dto_update_items__when_user_is_owner__update_the_list(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list0 = sample_data['lists'][0]
    lists_table().put_item(
        Item=list0
    )
    list_id = list0['id']
    new_items = ['item3', 'item4']

    res = ListsDto.update_items(list_id, new_items, tested_user_id)

    res_saved = lists_table().get_item(
        Key={
            'id': list_id
        }
    )

    assert res == new_items
    assert res_saved['Item']['items'] == new_items


def test_lists_dto_update_items__when_user_is_guests__update_the_list(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list1 = sample_data['lists'][1]
    lists_table().put_item(
        Item=list1
    )
    list_id = list1['id']
    new_items = ['item3', 'item4']

    res = ListsDto.update_items(list_id, new_items, tested_user_id)

    res_saved = lists_table().get_item(
        Key={
            'id': list_id
        }
    )

    assert res == new_items
    assert res_saved['Item']['items'] == new_items


def test_lists_dto_update_item__when_list_does_not_exist__raise_not_found_error(
        dynamodb_lists_table
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto

    with pytest.raises(NotFoundError):
        ListsDto.update_item('abcdef', 0, 'item3', tested_user_id)


def test_lists_dto_update_item__when_user_has_no_access__raise_not_found_error(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list0 = copy.deepcopy(sample_data['lists'][0])
    list0['userId'] = 'other_user_id'

    lists_table().put_item(
        Item=list0
    )

    with pytest.raises(NotFoundError):
        ListsDto.update_item(list0['id'], 0, 'item2', tested_user_id)


def test_lists_dto_update_item__when_user_is_owner__update_the_list(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list0 = sample_data['lists'][0]
    lists_table().put_item(
        Item=list0
    )
    list_id = list0['id']
    new_item = 'item3'
    item_idx = 1

    res = ListsDto.update_item(list_id, item_idx, new_item, tested_user_id)

    res_saved = lists_table().get_item(
        Key={
            'id': list_id
        }
    )

    assert res[item_idx] == new_item
    assert res_saved['Item']['items'][item_idx] == new_item


def test_lists_dto_update_item__when_user_is_guest__update_the_list(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list1 = sample_data['lists'][1]
    lists_table().put_item(
        Item=list1
    )
    list_id = list1['id']
    new_item = 'item3'
    item_idx = 1

    res = ListsDto.update_item(list_id, item_idx, new_item, tested_user_id)

    res_saved = lists_table().get_item(
        Key={
            'id': list_id
        }
    )

    assert res[item_idx] == new_item
    assert res_saved['Item']['items'][item_idx] == new_item