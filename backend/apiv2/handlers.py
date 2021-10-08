from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import ApiGatewayResolver
from aws_lambda_powertools.event_handler.api_gateway import ProxyEventType
from aws_lambda_powertools.event_handler.exceptions import BadRequestError
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.validation import envelopes

from aws_utils.event_parser import resolved_event_parser
from aws_utils.http_errors import http_errors_handler
from sf_shopping_list.api_models import ListModel, Invitation, NewList
from sf_shopping_list.data.dto.lists_dto import ListsDto

logger = Logger()
app = ApiGatewayResolver(proxy_type=ProxyEventType.APIGatewayProxyEventV2)


@app.get('/list')
def get_lists():
    assert isinstance(app.current_event, APIGatewayProxyEventV2)
    sub = _get_auth_user_sub(app.current_event)
    return ListsDto.get_all(sub)


@app.post('/list')
@resolved_event_parser(app, NewList, envelopes.API_GATEWAY_HTTP)
def create_list(body: NewList):
    assert isinstance(app.current_event, APIGatewayProxyEventV2)
    sub = _get_auth_user_sub(app.current_event)
    return ListsDto.create(body, sub)


@app.get('/list/<id>')
def get_list(id):
    assert isinstance(app.current_event, APIGatewayProxyEventV2)
    sub = _get_auth_user_sub(app.current_event)
    return ListsDto.get(id, sub)


@app.put('/list/<id>')
@resolved_event_parser(app, ListModel, envelopes.API_GATEWAY_HTTP)
def update_list(id, body):
    pass


@app.delete('/list/<id>')
def delete_list(id):
    pass


@app.post('/list/<id>/item')
def add_item(id):
    assert isinstance(app.current_event, APIGatewayProxyEventV2)
    sub = _get_auth_user_sub(app.current_event)
    new_item = app.current_event.decoded_body
    return ListsDto.add_item(id, new_item, sub)


@app.put('/list/<id>/item')
def update_item(id):
    assert isinstance(app.current_event, APIGatewayProxyEventV2)
    sub = _get_auth_user_sub(app.current_event)
    try:
        item_idx = int(app.current_event.get_query_string_value('idx'))
        new_item = app.current_event.decoded_body
        if new_item is None:
            raise ValueError('Missing body')
    except (ValueError, TypeError):
        raise BadRequestError('Missing data')

    return ListsDto.update_item(id, item_idx, new_item, sub)


@app.delete('/list/<id>/item')
def delete_item(id):
    assert isinstance(app.current_event, APIGatewayProxyEventV2)
    sub = _get_auth_user_sub(app.current_event)
    try:
        item_idx = int(app.current_event.get_query_string_value('idx'))
    except (ValueError, TypeError):
        raise BadRequestError('Missing data')

    return ListsDto.remove_item(id, item_idx, sub)


@app.post('/list/<id>/share')
@resolved_event_parser(app, Invitation, envelopes.API_GATEWAY_HTTP)
def share_list(id, body: Invitation):
    pass


@app.get('/s/<code>')
def accept_invitation(code):
    pass


def _get_auth_user_sub(event: APIGatewayProxyEventV2):
    return event.request_context.authorizer.jwt_claim['sub']


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@http_errors_handler
def lambda_handler(event, context):
    return app.resolve(event, context)
