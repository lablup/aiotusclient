import asyncio
from collections import OrderedDict
import io
import json
from unittest import mock

import aiohttp
from aioresponses import aioresponses
import pytest

from ai.backend.client.exceptions import BackendClientError
from ai.backend.client.request import Request, Response


@pytest.fixture
def mock_request_params(defconfig):
    return OrderedDict(
        method='GET',
        path='/function/item/',
        content=OrderedDict(test1='1'),
        config=defconfig
    )


def test_request_initialization(mock_request_params):
    rqst = Request(**mock_request_params)

    assert rqst.config == mock_request_params['config']
    assert rqst.method == mock_request_params['method']
    assert rqst.path == mock_request_params['path'].lstrip('/')
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


def test_send_and_read_response(dummy_endpoint):
    # Request.send() now calls Request.asend() internally.
    with aioresponses() as m:
        body = b'hello world'
        m.post(
            dummy_endpoint + 'function', status=200, body=body,
            headers={'Content-Type': 'text/plain; charset=utf-8',
                     'Content-Length': str(len(body))},
        )
        rqst = Request('POST', 'function')
        resp = rqst.send()
    assert isinstance(resp, Response)
    assert resp.status == 200
    assert resp.charset == 'utf-8'
    assert resp.content_type == 'text/plain'
    assert resp.text() == body.decode()
    assert resp.content_length == len(body)

    with aioresponses() as m:
        body = b'{"a": 1234, "b": null}'
        m.post(
            dummy_endpoint + 'function', status=200, body=body,
            headers={'Content-Type': 'application/json; charset=utf-8',
                     'Content-Length': str(len(body))},
        )
        rqst = Request('POST', 'function')
        resp = rqst.send()
    assert isinstance(resp, Response)
    assert resp.status == 200
    assert resp.charset == 'utf-8'
    assert resp.content_type == 'application/json'
    assert resp.text() == body.decode()
    assert resp.json() == {'a': 1234, 'b': None}
    assert resp.content_length == len(body)

    # Read content by chunks.
    with aioresponses() as m:
        body = b'hello world'
        m.post(
            dummy_endpoint + 'function', status=200, body=body,
            headers={'Content-Type': 'text/plain; charset=utf-8',
                     'Content-Length': str(len(body))},
        )
        rqst = Request('POST', 'function')
        resp = rqst.send()
    assert isinstance(resp, Response)
    assert resp.status == 200
    assert resp.charset == 'utf-8'
    assert resp.content_type == 'text/plain'
    assert resp.read(3) == b'hel'
    assert resp.read(2) == b'lo'
    assert not resp.at_stream_eof
    resp.read()
    assert resp.at_stream_eof
    with pytest.raises(AssertionError):
        assert resp.text()


def test_invalid_requests(dummy_endpoint):
    with aioresponses() as m:
        body = json.dumps({
            'type': 'https://api.backend.ai/probs/kernel-not-found',
            'title': 'Kernel Not Found',
        }).encode('utf8')
        m.post(
            dummy_endpoint, status=404, body=body,
            headers={'Content-Type': 'application/problem+json; charset=utf-8',
                     'Content-Length': str(len(body))},
        )
        rqst = Request('POST', '/')
        resp = rqst.send()
    assert isinstance(resp, Response)
    assert resp.status == 404
    assert resp.charset == 'utf-8'
    assert resp.content_type == 'application/problem+json'
    assert resp.text() == body.decode()
    assert resp.content_length == len(body)
    data = resp.json()
    assert data['type'] == 'https://api.backend.ai/probs/kernel-not-found'
    assert data['title'] == 'Kernel Not Found'


@pytest.mark.asyncio
async def test_asend_not_allowed_request_raises_error():
    rqst = Request('STRANGE', '/')
    with pytest.raises(AssertionError):
        await rqst.asend()


@pytest.mark.asyncio
async def test_asend_client_error(dummy_endpoint):
    with aioresponses() as m:
        m.post(dummy_endpoint,
               exception=aiohttp.ClientConnectionError())
        rqst = Request('POST', '/')
        with pytest.raises(BackendClientError):
            await rqst.asend()


@pytest.mark.asyncio
async def test_asend_cancellation(dummy_endpoint):
    with aioresponses() as m:
        m.post(dummy_endpoint,
               exception=asyncio.CancelledError())
        rqst = Request('POST', '/')
        with pytest.raises(asyncio.CancelledError):
            await rqst.asend()


@pytest.mark.asyncio
async def test_asend_timeout(dummy_endpoint):
    with aioresponses() as m:
        m.post(dummy_endpoint,
               exception=asyncio.TimeoutError())
        rqst = Request('POST', '/')
        with pytest.raises(asyncio.TimeoutError):
            await rqst.asend()


def test_response_initialization():
    body = b'my precious content \xea\xb0\x80..'
    protocol = mock.Mock(_reading_paused=False)
    stream = aiohttp.streams.StreamReader(protocol)
    stream.feed_data(body)
    stream.feed_eof()
    resp = Response(299, 'Something Done', stream_reader=stream,
                    content_type='text/plain')
    assert resp.status == 299
    assert resp.reason == 'Something Done'
    assert resp.content_type == 'text/plain'
    assert resp.text() == 'my precious content 가..'
    assert resp.content_length == len(body)
