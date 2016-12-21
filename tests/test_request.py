from collections import OrderedDict
from urllib.parse import urljoin

import aiohttp
import pytest
import requests
import simplejson as json

from sorna.exceptions import SornaAPIError
from sorna.request import Request, Response


@pytest.fixture
def req_params(defconfig):
    return dict(
        method='GET',
        path='/path/to/api/',
        data=OrderedDict(test1='1'),
        config=defconfig
    )


@pytest.fixture
def mock_sorna_resp(mocker):
    resp = mocker.Mock(spec=requests.Response)
    conf = {
        'status_code': 900,
        'reason': 'this is a test',
        'text': b'{"test1": 1, "test2": 2}',
        'headers': {
            'content-type': 'application/json',
            'content-length': len(b'{"test1": 1, "test2": 2}')
        }
    }
    resp.configure_mock(**conf)

    return resp, conf


@pytest.fixture
async def mock_async_sorna_resp(mocker):
    resp = mocker.Mock(spec=aiohttp.ClientResponse)
    conf = {
        'status': 900,
        'reason': 'this is a test',
        'body': b'{"test1": 1, "test2": 2}',
        'content_type': 'application/json',
    }
    resp.configure_mock(**conf)

    return resp


def test_request_initialization(req_params):
    req = Request(**req_params)

    assert req.config == req_params['config']
    assert req.method == req_params['method']
    assert req.path == req_params['path'][1:]
    assert req.data == req_params['data']
    assert 'Content-Type' in req.headers
    assert 'Date' in req.headers
    assert 'X-Sorna-Version' in req.headers
    assert req._content is None


def test_autofill_content_when_not_set(req_params):
    req = Request(**req_params)

    assert req._content is None
    assert req.content == json.dumps(req_params['data']).encode()
    assert req.headers['Content-Length'] == str(len(req.content))


def test_content_is_auto_set_to_blank_if_no_data(req_params):
    req_params['data'] = OrderedDict()
    req = Request(**req_params)

    assert req.content == b''


def test_cannot_set_content_if_data_exists(req_params):
    req = Request(**req_params)

    with pytest.raises(AssertionError):
        req.content = b'new-data'


def test_set_content_correctly(req_params):
    req_params['data'] = OrderedDict()
    req = Request(**req_params)
    new_data = b'new-data'

    assert not req.data
    req.content = new_data
    assert req.content == new_data
    assert req.headers['Content-Length'] == str(len(new_data))


def test_sign_update_authorization_headers_info(req_params):
    req = Request(**req_params)
    old_hdrs = req.headers

    assert 'Authorization' not in old_hdrs
    req.sign()
    assert 'Authorization' in req.headers


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
            mocker.ANY, req.build_url(), data=req.content, headers=req.headers)


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
        assert resp.text() == conf['text']
        assert resp.json() == json.loads(conf['text'])


@pytest.mark.asyncio
async def test_asend_not_allowed_request_raises_error(req_params):
    req_params['method'] = 'STRANGE'
    req = Request(**req_params)

    with pytest.raises(AssertionError):
        await req.asend()


@pytest.mark.asyncio
async def test_asend_with_appropriate_method(
        mocker, req_params, mock_async_sorna_resp):
    req = Request(**req_params)
    methods = Request._allowed_methods
    for method in methods:
        req.method = method

        mock_reqfunc = mocker.patch.object(
            aiohttp.ClientSession, method.lower(), autospec=True)
        mock_reqfunc.return_value = mock_async_sorna_resp

        assert mock_reqfunc.call_count == 0
        try:
            # TODO: Mocking the response of aiohttp request methods raises
            # exception. Have to think about smarter way to circumvent
            # this exception. However, it is not major concern for this unit
            # test.
            await req.asend()
        except SornaAPIError:
            pass
        mock_reqfunc.assert_called_once_with(
            mocker.ANY, req.build_url(), data=req.content, headers=req.headers)


@pytest.mark.asyncio
@pytest.mark.skip('not implemented yet')
async def test_asend_returns_appropriate_sorna_response(
        mocker, req_params, mock_sorna_resp):
    pass


def test_response_initialization(mock_sorna_resp):
    _, conf = mock_sorna_resp
    resp = Response(conf['status_code'], conf['reason'], conf['text'],
                    conf['headers']['content-type'],
                    conf['headers']['content-length'])

    assert resp.status == conf['status_code']
    assert resp.reason == conf['reason']
    assert resp.content_type == conf['headers']['content-type']
    assert resp.content_length == conf['headers']['content-length']
    assert resp.text() == conf['text']
    assert resp.json() == json.loads(conf['text'])
