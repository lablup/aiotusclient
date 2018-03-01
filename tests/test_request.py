from collections import OrderedDict
import io
from unittest import mock
from urllib.parse import urljoin

import aiohttp
from aioresponses import aioresponses
import asynctest
import pytest
import requests
import json

from .common import mock_coro, MockAsyncContextManager
from ai.backend.client.exceptions import BackendClientError
from ai.backend.client.request import Request, Response


@pytest.fixture
def req_params(defconfig):
    return OrderedDict(
        method='GET',
        path='/path/to/api/',
        content=OrderedDict(test1='1'),
        config=defconfig
    )


@pytest.fixture
def mock_sorna_resp():
    resp = mock.Mock(spec=requests.Response)
    content = b'{"test1": 1, "test2": 2}'
    conf = {
        'status_code': 900,
        'reason': 'this is a test',
        'content': content,
        'headers': {
            'content-type': 'application/json',
            'content-length': len(content),
        }
    }
    resp.configure_mock(**conf)

    return resp, conf


@pytest.fixture
def mock_sorna_aresp():
    conf = {
        'status': 900,
        'reason': 'this is a test',
        'read': mock_coro(b'{"test1": 1, "test2": 2}'),
        'content_type': 'application/json',
    }

    return MockAsyncContextManager(**conf), conf


def test_request_initialization(req_params):
    req = Request(**req_params)

    assert req.config == req_params['config']
    assert req.method == req_params['method']
    assert req.path == req_params['path'][1:]
    assert req.content == req_params['content']
    assert 'Date' in req.headers
    assert 'X-BackendAI-Version' in req.headers
    assert req._content == json.dumps(req_params['content']).encode('utf8')


def test_content_is_auto_set_to_blank_if_no_data(req_params):
    req_params = req_params.copy()
    req_params['content'] = None
    req = Request(**req_params)

    assert req.content_type == 'application/octet-stream'
    assert req.content == b''


def test_content_is_blank(req_params):
    req_params['content'] = OrderedDict()
    req = Request(**req_params)

    assert req.content_type == 'application/json'
    assert req.content == {}


def test_content_is_bytes(req_params):
    req_params['content'] = b'\xff\xf1'
    req = Request(**req_params)

    assert req.content_type == 'application/octet-stream'
    assert req.content == b'\xff\xf1'


def test_content_is_text(req_params):
    req_params['content'] = 'hello'
    req = Request(**req_params)

    assert req.content_type == 'text/plain'
    assert req.content == 'hello'


def test_content_is_files(req_params):
    files = [
        ('src', 'test1.txt', io.BytesIO(), 'application/octet-stream'),
        ('src', 'test2.txt', io.BytesIO(), 'application/octet-stream'),
    ]
    req_params['content'] = files
    req = Request(**req_params)

    assert req.content_type == 'multipart/form-data'
    assert req.content == files


def test_set_content_correctly(req_params):
    req_params['content'] = OrderedDict()
    req = Request(**req_params)
    new_data = b'new-data'

    assert not req.content
    req.content = new_data
    assert req.content == new_data
    assert req.headers['Content-Length'] == str(len(new_data))


def test_build_correct_url(req_params):
    config = req_params['config']
    req = Request(**req_params)

    major_ver = config.version.split('.', 1)[0]
    path = '/' + req.path if len(req.path) > 0 else ''

    assert req.build_url() == urljoin(config.endpoint, major_ver + path)


def test_send_not_allowed_request_raises_error(req_params):
    req_params['method'] = 'STRANGE'
    req = Request(**req_params)

    with pytest.raises(AssertionError):
        req.send()


def test_send_with_appropriate_method(mocker, req_params):
    req = Request(**req_params)
    methods = Request._allowed_methods
    for method in methods:
        req.method = method

        mock_reqfunc = mocker.patch.object(
            requests.Session, method.lower(), autospec=True)

        assert mock_reqfunc.call_count == 0
        req.send()
        mock_reqfunc.assert_called_once_with(
            mocker.ANY, req.build_url(), data=req._content, headers=req.headers)


def test_send_returns_appropriate_sorna_response(
        mocker, req_params, mock_sorna_resp):
    req = Request(**req_params)
    methods = Request._allowed_methods
    for method in methods:
        req.method = method

        mock_reqfunc = mocker.patch.object(
            requests.Session, method.lower(), autospec=True)
        mock_reqfunc.return_value, conf = mock_sorna_resp

        resp = req.send()

        assert resp.status == conf['status_code']
        assert resp.reason == conf['reason']
        assert resp.content_type == conf['headers']['content-type']
        assert resp.content_length == conf['headers']['content-length']
        assert resp.text() == conf['content'].decode()
        assert resp.json() == json.loads(conf['content'].decode())


@pytest.mark.asyncio
async def test_asend_not_allowed_request_raises_error(req_params):
    req_params['method'] = 'STRANGE'
    req = Request(**req_params)

    with pytest.raises(AssertionError):
        await req.asend()


@pytest.mark.asyncio
async def test_asend_with_appropriate_method(mocker, req_params):
    req = Request(**req_params)
    methods = Request._allowed_methods
    for method in methods:
        req.method = method

        mock_reqfunc = mocker.patch.object(
            aiohttp.ClientSession, method.lower(), autospec=True)

        assert mock_reqfunc.call_count == 0
        try:
            # Ignore exceptions in `async with` statement. We're only
            # interested in request call here.
            await req.asend()
        except BackendClientError:
            pass
        mock_reqfunc.assert_called_once_with(
            mocker.ANY, req.build_url(), data=req._content, headers=req.headers)


@pytest.mark.asyncio
async def test_asend_returns_appropriate_sorna_response(mocker, req_params,
                                                        mock_sorna_aresp):
    req = Request(**req_params)
    methods = Request._allowed_methods
    _, conf = mock_sorna_aresp
    for method in methods:
        req.method = method
        body = await conf['read']()

        with aioresponses() as m:
            getattr(m, method.lower())('http://127.0.0.1:8081/v2/path/to/api/',
                                       status=conf['status'], body=body)
            resp = await req.asend()

        assert isinstance(resp, Response)
        assert resp.status == conf['status']
        # NOTE: aioresponses does not support mocking this. :(
        # assert resp.reason == conf['reason']
        assert resp.content_type == conf['content_type']
        assert resp.content_length == len(body)
        assert resp.text() == body.decode()
        assert resp.json() == json.loads(body.decode())


def test_response_initialization(mock_sorna_resp):
    _, conf = mock_sorna_resp
    resp = Response(conf['status_code'], conf['reason'], conf['content'],
                    conf['headers']['content-type'],
                    conf['headers']['content-length'])

    assert resp.status == conf['status_code']
    assert resp.reason == conf['reason']
    assert resp.content_type == conf['headers']['content-type']
    assert resp.content_length == conf['headers']['content-length']
    assert resp.text() == conf['content'].decode()
    assert resp.json() == json.loads(conf['content'].decode())
