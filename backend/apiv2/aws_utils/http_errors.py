import functools

from sf_shopping_list.utils.errors import NotFoundError, NoAccessError, IncorrectRequestError

from aws_lambda_powertools.event_handler.exceptions import NotFoundError as AWSNotFoundError, UnauthorizedError, \
    BadRequestError


def http_errors_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotFoundError:
            raise AWSNotFoundError('Resource does not exist')
        except NoAccessError:
            raise UnauthorizedError('User has no access to this resource')
        except IncorrectRequestError:
            raise BadRequestError('Incorrect request')
    return wrapper
