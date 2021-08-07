from sf_shopping_list.api_models import ListModel
from sf_shopping_list.data.access.base_data import BaseDataAccessClass


class Lists(BaseDataAccessClass):

    @staticmethod
    def get_all():
        pass

    @staticmethod
    def get(id: int) -> ListModel:
        pass
