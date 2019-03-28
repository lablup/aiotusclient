import os

import pytest

from ai.backend.client.config import APIConfig, set_config


@pytest.fixture(autouse=True)
def defconfig():
    if os.environ.get('BACKEND_CLIENT_CLOUD_TEST'):
        c = APIConfig(endpoint='',
                      access_key='',
                      secret_key='')
    else:
        c = APIConfig(endpoint='http://127.0.0.1:8081',
                      access_key='AKIAIOSFODNN7EXAMPLE',
                      secret_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY')
    set_config(c)
    return c


@pytest.fixture
def userconfig():
    if os.environ.get('BACKEND_CLIENT_CLOUD_TEST'):
        c = APIConfig(endpoint='',
                      access_key='',
                      secret_key='')
    else:
        c = APIConfig(endpoint='http://127.0.0.1:8081',
                      access_key='AKIANABBDUSEREXAMPLE',
                      secret_key='C8qnIo29EZvXkPK_MXcuAakYTy4NYrxwmCEyNPlf')
    set_config(c)
    return c


@pytest.fixture
def example_keypair():
    if os.environ.get('BACKEND_CLIENT_CLOUD_TEST'):
        return ('', '')
    else:
        return ('AKIAIOSFODNN7EXAMPLE', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY')


@pytest.fixture
def user_keypair():
    if os.environ.get('BACKEND_CLIENT_CLOUD_TEST'):
        return ('', '')
    else:
        return ('AKIAIOSFODNN7EXAMPLE', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY')


@pytest.fixture
def dummy_endpoint(defconfig):
    return str(defconfig.endpoint) + '/'
