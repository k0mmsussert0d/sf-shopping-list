import os
from unittest import mock

import pytest
import yaml


@pytest.fixture(autouse=True, scope='session')
def mock_env_vars():
    with mock.patch.dict(os.environ, {
        'DYNAMODB_MAIN_TABLE': 'ListsTable'
    }):
        yield


@pytest.fixture(scope='session')
def sls_shared_stack():
    cwd = os.path.relpath(__file__)
    with open(os.path.join(cwd, '../../shared/serverless.yml')) as shared_sls:
        yield yaml.load(shared_sls, yaml.FullLoader)
