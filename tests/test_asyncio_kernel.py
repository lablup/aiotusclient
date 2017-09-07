from unittest import mock

import aiohttp
import asynctest
import pytest

from ai.backend.client.asyncio.kernel import (
    create_kernel, destroy_kernel, restart_kernel, get_kernel_info,
    execute_code, stream_pty, StreamPty
)
from ai.backend.client.compat import token_hex
from ai.backend.client.exceptions import BackendAPIError, BackendClientError
from ai.backend.client.request import Request


@pytest.mark.asyncio
async def test_create_kernel_url():
    mock_resp = asynctest.MagicMock(spec=aiohttp.ClientResponse)
    mock_resp.status = 201
    mock_resp.json = asynctest.MagicMock()

    mock_req_obj = asynctest.MagicMock(spec=Request)
    mock_req_obj.asend.return_value = mock_resp

    with asynctest.patch('ai.backend.client.kernel.Request',
                         return_value=mock_req_obj) as mock_req_cls:
        await create_kernel('python')

        mock_req_cls.assert_called_once_with(
            'POST', '/kernel/create', mock.ANY)
        mock_req_obj.asend.assert_called_once_with()
        mock_req_obj.asend.return_value.json.assert_called_once_with()


@pytest.mark.asyncio
async def test_create_kernel_return_id_only():
    mock_resp = asynctest.MagicMock(spec=aiohttp.ClientResponse)
    mock_resp.status = 201
    mock_resp.json = lambda: {'kernelId': 'mock_kernel_id'}

    mock_req_obj = asynctest.MagicMock(spec=Request)
    mock_req_obj.asend.return_value = mock_resp

    with asynctest.patch('ai.backend.client.kernel.Request',
                         return_value=mock_req_obj) as mock_req_cls:
        k = await create_kernel('python')

        assert k.kernel_id == mock_resp.json()['kernelId']


@pytest.mark.asyncio
async def test_create_kernel_raises_err_with_abnormal_status():
    mock_req_obj = asynctest.MagicMock(spec=Request)
    mock_req_obj.asend.return_value = asynctest.MagicMock(status=400)
    with asynctest.patch('ai.backend.client.kernel.Request',
                         return_value=mock_req_obj):
        with pytest.raises(BackendAPIError):
            await create_kernel('python')


@pytest.mark.asyncio
async def test_destroy_kernel_url():
    mock_req_obj = asynctest.MagicMock(spec=Request)
    mock_req_obj.asend.return_value = asynctest.MagicMock(status=204)
    kernel_id = token_hex(12)
    with asynctest.patch('ai.backend.client.kernel.Request',
                         return_value=mock_req_obj) as mock_req_cls:
        await destroy_kernel(kernel_id)
        mock_req_cls.assert_called_once_with(
            'DELETE', '/kernel/{}'.format(kernel_id))


@pytest.mark.asyncio
async def test_destroy_kernel_raises_err_with_abnormal_status():
    mock_req_obj = asynctest.MagicMock(spec=Request)
    mock_req_obj.asend.return_value = asynctest.MagicMock(status=400)
    with asynctest.patch('ai.backend.client.kernel.Request',
                         return_value=mock_req_obj):
        with pytest.raises(BackendAPIError):
            await destroy_kernel('mykernel')


@pytest.mark.asyncio
async def test_restart_kernel_url():
    mock_req_obj = asynctest.MagicMock(spec=Request)
    mock_req_obj.asend.return_value = asynctest.MagicMock(status=204)
    kernel_id = token_hex(12)
    with asynctest.patch('ai.backend.client.kernel.Request',
                         return_value=mock_req_obj) as mock_req_cls:
        await restart_kernel(kernel_id)
        mock_req_cls.assert_called_once_with(
            'PATCH', '/kernel/{}'.format(kernel_id))


@pytest.mark.asyncio
async def test_restart_kernel_raises_err_with_abnormal_status():
    mock_req_obj = asynctest.MagicMock(spec=Request)
    mock_req_obj.asend.return_value = asynctest.MagicMock(status=400)
    with asynctest.patch('ai.backend.client.kernel.Request',
                         return_value=mock_req_obj):
        with pytest.raises(BackendAPIError):
            await restart_kernel('mykernel')


@pytest.mark.asyncio
async def test_get_kernel_info_url():
    mock_req_obj = asynctest.MagicMock(spec=Request)
    mock_req_obj.asend.return_value = asynctest.MagicMock(status=200)
    kernel_id = token_hex(12)
    with asynctest.patch('ai.backend.client.kernel.Request',
                         return_value=mock_req_obj) as mock_req_cls:
        await get_kernel_info(kernel_id)
        mock_req_cls.assert_called_once_with(
            'GET', '/kernel/{}'.format(kernel_id))


@pytest.mark.asyncio
async def test_get_kernel_info_raises_err_with_abnormal_status():
    mock_req_obj = asynctest.MagicMock(spec=Request)
    mock_req_obj.asend.return_value = asynctest.MagicMock(status=400)
    with asynctest.patch('ai.backend.client.kernel.Request',
                         return_value=mock_req_obj):
        with pytest.raises(BackendAPIError):
            await get_kernel_info('mykernel')


@pytest.mark.asyncio
async def test_execute_code_url():
    mock_req_obj = asynctest.MagicMock(spec=Request)
    mock_req_obj.asend.return_value = asynctest.MagicMock(status=200)
    kernel_id = token_hex(12)
    with asynctest.patch('ai.backend.client.kernel.Request',
                         return_value=mock_req_obj) as mock_req_cls:
        await execute_code(kernel_id, 'hello')
        mock_req_cls.assert_called_once_with(
            'POST', '/kernel/{}'.format(kernel_id),
            {'mode': 'query', 'code': 'hello'})


@pytest.mark.asyncio
async def test_execute_code_raises_err_with_abnormal_status():
    mock_req_obj = asynctest.MagicMock(spec=Request)
    mock_req_obj.asend.return_value = asynctest.MagicMock(status=400)
    with asynctest.patch('ai.backend.client.kernel.Request',
                         return_value=mock_req_obj) as mock_req_cls:
        with pytest.raises(BackendAPIError):
            await execute_code('mykernel', 'hello')


@pytest.mark.asyncio
async def test_stream_pty(mocker):
    mock_req_obj = asynctest.MagicMock(spec=Request)
    sess, ws = object(), object()
    mock_req_obj.connect_websocket.return_value = (sess, ws)
    kernel_id = token_hex(12)
    with asynctest.patch('ai.backend.client.asyncio.kernel.Request',
                         return_value=mock_req_obj) as mock_req_cls:
        stream = await stream_pty(kernel_id)
        mock_req_cls.assert_called_once_with(
            'GET', '/stream/kernel/{}/pty'.format(kernel_id))
        mock_req_obj.connect_websocket.assert_called_once_with()
        assert isinstance(stream, StreamPty)
        assert stream.sess is sess
        assert stream.ws is ws


@pytest.mark.asyncio
async def test_stream_pty_raises_error_with_abnormal_status(mocker):
    mock_req_obj = asynctest.MagicMock(spec=Request)
    mock_exception = aiohttp.ClientResponseError(
        None, None, code=400,
        message='emulated-handshake-error')
    mock_req_obj.connect_websocket = \
        asynctest.MagicMock(side_effect=mock_exception)
    with asynctest.patch('ai.backend.client.asyncio.kernel.Request',
                         return_value=mock_req_obj) as mock_req_cls:
        with pytest.raises(BackendClientError):
            await stream_pty('mykernel')
