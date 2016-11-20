import socket

import pytest

from sorna.config import APIConfig, set_config


@pytest.fixture
def unused_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


@pytest.fixture
def defconfig():
    c = APIConfig(endpoint='http://127.0.0.1:8081',
                  access_key='AKIAIOSFODNN7EXAMPLE',
                  secret_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY')
    set_config(c)
    return c
