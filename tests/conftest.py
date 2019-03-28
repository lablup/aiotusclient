import os

import pytest

from ai.backend.client.config import APIConfig, set_config


@pytest.fixture(autouse=True)
def defconfig():
    if os.environ.get('BACKEND_CLIENT_CLOUD_TEST'):
        c = APIConfig(endpoint='https://api-beta.backend.ai',
                      access_key='AKIAJOJPGI3MVIZ4LH3R',
                      secret_key='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')
    else:
        c = APIConfig(endpoint='http://127.0.0.1:8081',
                      access_key='AKIAIOSFODNN7EXAMPLE',
                      secret_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY')
    set_config(c)
    return c


@pytest.fixture
def userconfig():
    if os.environ.get('BACKEND_CLIENT_CLOUD_TEST'):
        c = APIConfig(endpoint='https://api-beta.backend.ai',
                      access_key='AKIAV7B7NVO3XZBKHUTN',
                      secret_key='K0wb3vYYn_6QvjTWsMNdbOi_TzQZIb7XuUMw1vi8')
    else:
        c = APIConfig(endpoint='http://127.0.0.1:8081',
                      access_key='AKIANABBDUSEREXAMPLE',
                      secret_key='C8qnIo29EZvXkPK_MXcuAakYTy4NYrxwmCEyNPlf')
    set_config(c)
    return c


@pytest.fixture
def example_keypair():
    if os.environ.get('BACKEND_CLIENT_CLOUD_TEST'):
        return ('AKIAJOJPGI3MVIZ4LH3R', 'lnbJlkWn9ddSD2Jxr0a6oQ7KYjIHnS9ZIhxH7LlM')
    else:
        return ('AKIAIOSFODNN7EXAMPLE', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY')


@pytest.fixture
def user_keypair():
    if os.environ.get('BACKEND_CLIENT_CLOUD_TEST'):
        return ('AKIAV7B7NVO3XZBKHUTN', 'K0wb3vYYn_6QvjTWsMNdbOi_TzQZIb7XuUMw1vi8')
    else:
        return ('AKIAIOSFODNN7EXAMPLE', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY')


@pytest.fixture
def dummy_endpoint(defconfig):
    return str(defconfig.endpoint) + '/'
