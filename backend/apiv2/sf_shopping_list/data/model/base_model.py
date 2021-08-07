from aws_lambda_powertools.utilities.parser import BaseModel as PydanticBaseModel
from orjson import orjson


def _orjson_dumps(val, *, default):
    return orjson.dumps(val, default=default).decode()


class BaseModel(PydanticBaseModel):

    class Config:
        json_loads = orjson.loads
        json_dumps = _orjson_dumps

    @classmethod
    def from_db_doc(cls, doc: dict):
        return cls.parse_obj(doc)
