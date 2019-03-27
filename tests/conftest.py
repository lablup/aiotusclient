import pytest

from ai.backend.client.config import APIConfig, set_config


@pytest.fixture(autouse=True)
def defconfig():
    # c = APIConfig(endpoint='http://127.0.0.1:8081',
    #               access_key='AKIAIOSFODNN7EXAMPLE',
    #               secret_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY')
    c = APIConfig(endpoint='https://api-beta.backend.ai',
                  access_key='AKIAJOJPGI3MVIZ4LH3R',
                  secret_key='lnbJlkWn9ddSD2Jxr0a6oQ7KYjIHnS9ZIhxH7LlM')
    set_config(c)
    return c


@pytest.fixture
def example_keypair():
    # return ('AKIAIOSFODNN7EXAMPLE', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY')
    return ('AKIAJOJPGI3MVIZ4LH3R', 'lnbJlkWn9ddSD2Jxr0a6oQ7KYjIHnS9ZIhxH7LlM')


@pytest.fixture
def dummy_endpoint(defconfig):
    return str(defconfig.endpoint) + '/'
