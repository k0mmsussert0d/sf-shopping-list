from abc import ABC
from contextlib import contextmanager

from botocore.exceptions import ClientError

from sf_shopping_list.utils.errors import NotFoundError


class BaseDataAccessClass(ABC):
    @staticmethod
    @contextmanager
    def _handle_conditional_check_fail():
        try:
            yield
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise NotFoundError('User is not authorized to modify this resource or it does not exist')
            else:
                raise e
