import json
from unittest import mock
from unittest.mock import PropertyMock, MagicMock

from aws_lambda_powertools.event_handler import ApiGatewayResolver
from aws_lambda_powertools.utilities.data_classes.common import BaseProxyEvent
from aws_lambda_powertools.utilities.validation import envelopes

from sf_shopping_list.api_models import NewList
from aws_utils.event_parser import resolved_event_parser
from events.__init__ import api_gateway_v2_event

app = ApiGatewayResolver()


@resolved_event_parser(app, NewList, envelopes.API_GATEWAY_HTTP)
def test(i, body):
    return i, body


if __name__ == '__main__':
    mocked_value = MagicMock(spec=BaseProxyEvent)
    mocked_json_body = PropertyMock(return_value=json.loads(api_gateway_v2_event['body']))
    type(mocked_value).json_body = mocked_json_body
    app.current_event = None
    with mock.patch.object(app, 'current_event', mocked_value):
        print(test(1))
