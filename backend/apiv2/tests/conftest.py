from unittest import mock

import yaml

from boto3_mocks import *


def _get_path_in_cwd(rel_path):
    cwd = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(cwd, rel_path)


def _load_yaml(path):
    with open(_get_path_in_cwd(path)) as yml:
        return yaml.load(yml, yaml.FullLoader)


@pytest.fixture(autouse=True, scope='session')
def mock_env_vars():
    with mock.patch.dict(os.environ, {
        'DYNAMODB_MAIN_TABLE': 'ListsTable'
    }):
        yield


@pytest.fixture(scope='session')
def sls_shared_stack():
    yield _load_yaml('../../shared/serverless.yml')


@pytest.fixture(scope='session')
def sample_data():
    yield _load_yaml('./data.yaml')
