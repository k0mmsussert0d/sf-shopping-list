from datetime import datetime

from sf_shopping_list.api_models import ListModel
from sf_shopping_list.data.model.list_doc import ListDocModel


class ListMappers:

    @staticmethod
    def map_doc_to_dto(doc: ListDocModel) -> ListModel:
        return ListModel.parse_obj({
            **doc.dict(),
            'createdAt': datetime.fromtimestamp(doc.createdAt)
        })

    @staticmethod
    def map_dto_to_doc(dto: ListModel) -> ListDocModel:
        return ListDocModel.parse_obj({
            **dto.dict(),
            'createdAt': int(dto.createdAt.timestamp())
        })
