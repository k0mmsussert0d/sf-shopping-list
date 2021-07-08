from typing import Union


def get_attribute(attr_list: list, attr_name: str, default: Union[str, int, bool] = None) -> Union[str, int, bool]:
    try:
        return list(filter(lambda x: x['Name'] == attr_name, attr_list))[0]['Value']
    except IndexError as e:
        if default:
            return default
        else:
            raise e
