from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import ApiGatewayResolver
from aws_lambda_powertools.event_handler.api_gateway import ProxyEventType
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.validation import envelopes

from sf_shopping_list.api_models import ListModel, Invitation
from aws_utils.event_parser import resolved_event_parser

logger = Logger()
app = ApiGatewayResolver(proxy_type=ProxyEventType.APIGatewayProxyEventV2)


@app.get('/list')
def get_lists():
    pass


@app.post('/list')
@resolved_event_parser(app, ListModel, envelopes.API_GATEWAY_HTTP)
def create_list(body: ListModel):
    pass


@app.get('/list/<id>')
def get_list(id):
    pass


@app.put('/list/<id>')
@resolved_event_parser(app, ListModel, envelopes.API_GATEWAY_HTTP)
def update_list(id, body):
    pass


@app.delete('/list/<id>')
def delete_list(id):
    pass


@app.post('/list/<id>/share')
@resolved_event_parser(app, Invitation, envelopes.API_GATEWAY_HTTP)
def share_list(id, body: Invitation):
    pass


@app.get('/s/<code>')
def accept_invitation(code):
    pass


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
def lambda_handler(event, context):
    return app.resolve(event, context)
