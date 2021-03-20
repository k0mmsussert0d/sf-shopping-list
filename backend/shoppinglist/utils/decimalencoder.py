import decimal
import json
from collections import abc


# This is a workaround for: http://bugs.python.org/issue16535
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        elif isinstance(obj, abc.Set):
            return list(obj)
        return super(DecimalEncoder, self).default(obj)
