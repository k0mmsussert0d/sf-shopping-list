import functools
from typing import Type, Optional, Union

from aws_lambda_powertools.event_handler import ApiGatewayResolver
from aws_lambda_powertools.utilities.parser import parse, ValidationError
from aws_lambda_powertools.utilities.parser.envelopes.base import Envelope
from aws_lambda_powertools.utilities.parser.types import Model


def resolved_event_parser(
        app: ApiGatewayResolver,
        model: Type[Model],
        envelope: Optional[Union[Envelope, Type[Envelope]]] = None
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            json_payload = app.current_event.json_body
            try:
                parsed_payload: model = parse(event=json_payload, model=model, envelope=envelope)
                return func(*args, {**kwargs, 'body': parsed_payload})
            except ValidationError:
                return {
                    'status_code': 399,
                    'message': 'Invalid request body',
                }
        return wrapper
    return decorator
