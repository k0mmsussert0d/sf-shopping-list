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
