import copy
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from sf_shopping_list.api_models import NewList, ListModel
from sf_shopping_list.data.model.list_doc import ListDocModel
from sf_shopping_list.data.model.user_to_lists_doc import UserToListsDocModel
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
other_user_id = '1d564127-9f04-47d4-a60c-61e4b8b6cf83'


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


def test_lists_dto_update__when_list_does_not_exist__return_none(
        dynamodb_lists_table
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto

    new_list = ListModel(
        id='ABCdef',
        userId=tested_user_id,
        listName='list name',
        createdAt=datetime.utcnow(),
        items=['item0', 'item1'],
        guests=[]
    )

    assert ListsDto.update('ABCdef', new_list, tested_user_id) is None


def test_lists_dto_update__when_user_has_no_access__raise_no_access_error(
        dynamodb_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list2 = sample_data['lists'][2]
    lists_table().put_item(
        Item=list2
    )

    new_list = ListModel.parse_obj(list2)

    with pytest.raises(NoAccessError):
        ListsDto.update(new_list.id, new_list, tested_user_id)


def test_lists_dto_update__when_user_is_owner__then_update_list(
        dynamodb_lists_table,
        dynamodb_user_to_lists_table,
        sample_data
):
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.db.lists import Lists
    from sf_shopping_list.data.clients.dynamodb import lists_table
    from sf_shopping_list.data.clients.dynamodb import user_to_lists_table

    list0 = sample_data['lists'][0]
    new_list0 = ListModel.parse_obj(list0)

    Lists.save(ListMappers.map_dto_to_doc(new_list0))

    # owner can change items, guests and listName
    new_list0.items = [
        'item4', 'item5', 'item6'
    ]
    new_list0.guests = {other_user_id}
    new_list0.listName = 'new list name'
    new_list0_res = ListsDto.update(new_list0.id, new_list0, new_list0.userId)
    new_list0_saved = lists_table().get_item(
        Key={
            'id': new_list0.id
        }
    )

    # updated list is returned
    assert new_list0_res == new_list0

    # updated list is saved
    assert ListDocModel.from_db_doc(new_list0_saved['Item']) == ListMappers.map_dto_to_doc(new_list0)

    # if guests were added, so their user_to_lists entries were updated
    other_user_lists = user_to_lists_table().get_item(
        Key={
            'user_id': other_user_id
        }
    )

    assert new_list0.id in UserToListsDocModel.from_db_doc(other_user_lists['Item']).lists

    # try removing guest
    new_list0.guests = set()
    new_list0_res = ListsDto.update(new_list0.id, new_list0, new_list0.userId)
    new_list0_saved = lists_table().get_item(
        Key={
            'id': new_list0.id
        }
    )

    assert new_list0_res == new_list0
    assert ListDocModel.from_db_doc(new_list0_saved['Item']) == ListMappers.map_dto_to_doc(new_list0)

    # guests should have their user_to_lists entries updated
    other_user_lists = user_to_lists_table().get_item(
        Key={
            'user_id': other_user_id
        }
    )

    assert new_list0.id not in UserToListsDocModel.from_db_doc(other_user_lists['Item']).lists

    # try adding guest back
    new_list0.guests = {other_user_id}
    new_list0_res = ListsDto.update(new_list0.id, new_list0, new_list0.userId)
    new_list0_saved = lists_table().get_item(
        Key={
            'id': new_list0.id
        }
    )

    assert new_list0_res == new_list0
    assert ListDocModel.from_db_doc(new_list0_saved['Item']) == ListMappers.map_dto_to_doc(new_list0)

    # guests should have their user_to_lists entries updated
    other_user_lists = user_to_lists_table().get_item(
        Key={
            'user_id': other_user_id
        }
    )

    # immutable fields changes should be ignored
    original_new_list_0 = new_list0.copy()
    new_list0.id = 'foo'
    new_list0.createdAt = datetime.utcnow()
    new_list0.userId = other_user_id

    new_list0_res = ListsDto.update(original_new_list_0.id, new_list0, original_new_list_0.userId)
    new_list_0_saved = lists_table().get_item(
        Key={
            'id': new_list0.id
        }
    )

    assert new_list0_res == original_new_list_0
    assert ListDocModel.from_db_doc(new_list_0_saved['Item']) == ListMappers.map_dto_to_doc(original_new_list_0)

    assert new_list0.id in UserToListsDocModel.from_db_doc(other_user_lists['Item']).lists


def test_lists_dto_update__when_user_is_guest__and_updates_only_items__then_update_list(
        dynamodb_lists_table,
        dynamodb_user_to_lists_table,
        sample_data
):
    from sf_shopping_list.data.db.lists import Lists
    from sf_shopping_list.data.dto.lists_dto import ListsDto
    from sf_shopping_list.data.clients.dynamodb import lists_table

    list1 = sample_data['lists'][1]
    new_list1 = ListModel.parse_obj(list1)

    Lists.save(ListMappers.map_dto_to_doc(new_list1))

    # guest is allowed to change items
    new_list1.items = ['item3', 'item4', 'item5']

    new_list1_res = ListsDto.update(new_list1.id, new_list1, tested_user_id)
    new_list1_saved = lists_table().get_item(
        Key={
            'id': new_list1.id
        }
    )

    assert new_list1_res == new_list1
    assert ListDocModel.from_db_doc(new_list1_saved['Item']) == ListMappers.map_dto_to_doc(new_list1)

    # guest is not allowed to modify guests list or name
    new_list1.guests += 'some_other_user_id'
    with pytest.raises(NoAccessError):
        ListsDto.update(new_list1.id, new_list1, tested_user_id)

    new_list1.listName = 'new list name'
    with pytest.raises(NoAccessError):
        ListsDto.update(new_list1.id, new_list1, tested_user_id)


def test_lists_dto_update__when_user_is_guest__and_updates_guests_or_name__then_raise_no_access_error(
        dynamodb_lists_table,
        dynamodb_user_to_lists_table,
        sample_data
):
    from sf_shopping_list.data.db.lists import Lists
    from sf_shopping_list.data.dto.lists_dto import ListsDto

    list1 = sample_data['lists'][1]
    new_list1 = ListModel.parse_obj(list1)

    Lists.save(ListMappers.map_dto_to_doc(new_list1))

    # guest is not allowed to modify guests list or name
    new_list1.guests += 'some_other_user_id'
    with pytest.raises(NoAccessError):
        ListsDto.update(new_list1.id, new_list1, tested_user_id)

    new_list1.listName = 'new list name'
    with pytest.raises(NoAccessError):
        ListsDto.update(new_list1.id, new_list1, tested_user_id)