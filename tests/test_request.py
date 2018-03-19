import asyncio
from collections import OrderedDict
import io
import json
from unittest import mock

import aiohttp
from asynctest import CoroutineMock, MagicMock, patch
import pytest
import requests

from ai.backend.client.exceptions import BackendClientError
from ai.backend.client.request import Request, Response


@pytest.fixture
def mock_request_params(defconfig):
    return OrderedDict(
        method='GET',
        path='/path/to/api/',
        content=OrderedDict(test1='1'),
        config=defconfig
    )


@pytest.fixture
def mock_requests_response():
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
def mock_aiohttp_response():

    def mocker(side_effect=None):
        ctx = MagicMock()
        resp = MagicMock()
        resp.status = 900
        resp.reason = 'Testing'
        resp.content_type = 'application/json'
        resp._test_body = b'{"test1": 1, "test2": 2}'  # for test codes
        if side_effect is None:
            resp.read = CoroutineMock(return_value=resp._test_body)
        else:
            resp.read = CoroutineMock(side_effect=side_effect)
        ctx.return_value.__aenter__.return_value = resp
        ctx._test_response = resp  # for test codes
        return ctx

    return mocker


def test_request_initialization(mock_request_params):
    rqst = Request(**mock_request_params)

    assert rqst.config == mock_request_params['config']
    assert rqst.method == mock_request_params['method']
    assert rqst.path == mock_request_params['path'][1:]
    assert rqst.content == mock_request_params['content']
    assert 'X-BackendAI-Version' in rqst.headers
    assert rqst._content == json.dumps(mock_request_params['content']).encode('utf8')


def test_content_is_auto_set_to_blank_if_no_data(mock_request_params):
    mock_request_params = mock_request_params.copy()
    mock_request_params['content'] = None
    rqst = Request(**mock_request_params)

    assert rqst.content_type == 'application/octet-stream'
    assert rqst.content == b''


def test_content_is_blank(mock_request_params):
    mock_request_params['content'] = OrderedDict()
    rqst = Request(**mock_request_params)

    assert rqst.content_type == 'application/json'
    assert rqst.content == {}


def test_content_is_bytes(mock_request_params):
    mock_request_params['content'] = b'\xff\xf1'
    rqst = Request(**mock_request_params)

    assert rqst.content_type == 'application/octet-stream'
    assert rqst.content == b'\xff\xf1'


def test_content_is_text(mock_request_params):
    mock_request_params['content'] = 'hello'
    rqst = Request(**mock_request_params)

    assert rqst.content_type == 'text/plain'
    assert rqst.content == 'hello'


def test_content_is_files(mock_request_params):
    files = [
        ('src', 'test1.txt', io.BytesIO(), 'application/octet-stream'),
        ('src', 'test2.txt', io.BytesIO(), 'application/octet-stream'),
    ]
    mock_request_params['content'] = files
    rqst = Request(**mock_request_params)

    assert rqst.content_type == 'multipart/form-data'
    assert rqst.content == files


def test_set_content_correctly(mock_request_params):
    mock_request_params['content'] = OrderedDict()
    rqst = Request(**mock_request_params)
    new_data = b'new-data'

    assert not rqst.content
    rqst.content = new_data
    assert rqst.content == new_data
    assert rqst.headers['Content-Length'] == str(len(new_data))


def test_build_correct_url(mock_request_params):
    config = mock_request_params['config']
    rqst = Request(**mock_request_params)

    major_ver = config.version.split('.', 1)[0]
    path = '/' + rqst.path if len(rqst.path) > 0 else ''

    canonical_url = 'http://127.0.0.1:8081/path/{0}{1}'.format(major_ver, path)
    assert rqst.build_url() == canonical_url


def test_send_not_allowed_request_raises_error(mock_request_params):
    mock_request_params['method'] = 'STRANGE'
    rqst = Request(**mock_request_params)

    with pytest.raises(AssertionError):
        rqst.send()


def test_send(mocker, mock_request_params):
    rqst = Request(**mock_request_params)
    methods = Request._allowed_methods
    for method in methods:
        rqst.method = method

        mock_reqfunc = mocker.patch.object(
            requests.Session, method.lower(), autospec=True)

        assert mock_reqfunc.call_count == 0
        rqst.send()
        mock_reqfunc.assert_called_once_with(
            mocker.ANY, rqst.build_url(),
            data=rqst._content, headers=rqst.headers)


def test_send_and_read_response(
        mocker, mock_request_params, mock_requests_response):
    rqst = Request(**mock_request_params)
    methods = Request._allowed_methods
    for method in methods:
        rqst.method = method

        mock_reqfunc = mocker.patch.object(
            requests.Session, method.lower(), autospec=True)
        mock_reqfunc.return_value, conf = mock_requests_response

        resp = rqst.send()

        assert resp.status == conf['status_code']
        assert resp.reason == conf['reason']
        assert resp.content_type == conf['headers']['content-type']
        assert resp.content_length == conf['headers']['content-length']
        assert resp.text() == conf['content'].decode()
        assert resp.json() == json.loads(conf['content'].decode())


@pytest.mark.asyncio
async def test_asend_not_allowed_request_raises_error(mock_request_params):
    mock_request_params['method'] = 'STRANGE'
    rqst = Request(**mock_request_params)
    with pytest.raises(AssertionError):
        await rqst.asend()


@pytest.mark.asyncio
async def test_asend_and_read_response(mocker, mock_request_params,
                                       mock_aiohttp_response):
    rqst = Request(**mock_request_params)
    methods = Request._allowed_methods
    mock_rqst_ctx = mock_aiohttp_response()
    mock_response = mock_rqst_ctx._test_response
    for method in methods:
        rqst.method = method
        with patch('aiohttp.ClientSession.request',
                   new=mock_rqst_ctx) as mock_request:
            resp = await rqst.asend()
            mock_request.assert_called_with(
                method, rqst.build_url(),
                data=rqst._content, headers=rqst.headers)
            assert isinstance(resp, Response)
            body = mock_response._test_body
            assert resp.status == mock_response.status
            assert resp.reason == mock_response.reason
            assert resp.content_type == mock_response.content_type
            assert resp.content_length == len(body)
            assert resp.text() == body.decode()
            assert resp.json() == json.loads(body.decode())


@pytest.mark.asyncio
async def test_asend_client_error(mock_request_params, mock_aiohttp_response):
    rqst = Request(**mock_request_params)
    mock_rqst_ctx = mock_aiohttp_response(side_effect=aiohttp.ClientConnectionError)
    with patch('aiohttp.ClientSession.request', new=mock_rqst_ctx):
        with pytest.raises(BackendClientError):
            await rqst.asend()


@pytest.mark.asyncio
async def test_asend_cancellation(mock_request_params, mock_aiohttp_response):
    rqst = Request(**mock_request_params)
    mock_rqst_ctx = mock_aiohttp_response(side_effect=asyncio.CancelledError)
    with patch('aiohttp.ClientSession.request', new=mock_rqst_ctx):
        with pytest.raises(asyncio.CancelledError):
            await rqst.asend()


@pytest.mark.asyncio
async def test_asend_timeout(mock_request_params, mock_aiohttp_response):
    rqst = Request(**mock_request_params)
    mock_rqst_ctx = mock_aiohttp_response(side_effect=asyncio.TimeoutError)
    with patch('aiohttp.ClientSession.request', new=mock_rqst_ctx):
        with pytest.raises(asyncio.TimeoutError):
            await rqst.asend()


def test_response_initialization(mock_requests_response):
    _, conf = mock_requests_response
    resp = Response(conf['status_code'], conf['reason'], conf['content'],
                    conf['headers']['content-type'],
                    conf['headers']['content-length'])

    assert resp.status == conf['status_code']
    assert resp.reason == conf['reason']
    assert resp.content_type == conf['headers']['content-type']
    assert resp.content_length == conf['headers']['content-length']
    assert resp.text() == conf['content'].decode()
    assert resp.json() == json.loads(conf['content'].decode())
