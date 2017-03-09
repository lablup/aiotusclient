import secrets
from unittest import mock

import pytest

from sorna.exceptions import SornaAPIError
from sorna.kernel import (
    create_kernel, destroy_kernel, restart_kernel, get_kernel_info,
    execute_code
)


def test_create_kernel_url(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mocker.MagicMock(status=201,
                                                      json=mock.MagicMock())
    mock_req = mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    create_kernel('python')

    mock_req.assert_called_once_with('POST', '/kernel/create', mocker.ANY)
    mock_req_obj.sign.assert_called_once_with()
    mock_req_obj.send.assert_called_once_with()
    mock_req_obj.send.return_value.json.assert_called_once_with()


def test_create_kernel_return_id_only(mocker):
    mock_json_func = lambda: {'kernelId': 'mock_kernel_id'}
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(
        status=201, json=mock_json_func
    )
    mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    k = create_kernel('python')

    assert k.kernel_id == mock_json_func()['kernelId']


def test_create_kernel_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    with pytest.raises(SornaAPIError):
        create_kernel('python')


def test_destroy_kernel_url(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=204)
    mock_req = mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    kernel_id = secrets.token_hex(12)
    destroy_kernel(kernel_id)

    mock_req.assert_called_once_with('DELETE', f'/kernel/{kernel_id}')
    mock_req_obj.sign.assert_called_once_with()
    mock_req_obj.send.assert_called_once_with()


def test_destroy_kernel_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    kernel_id = secrets.token_hex(12)
    with pytest.raises(SornaAPIError):
        destroy_kernel(kernel_id)


def test_restart_kernel_url(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=204)
    mock_req = mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    kernel_id = secrets.token_hex(12)
    restart_kernel(kernel_id)

    mock_req.assert_called_once_with('PATCH', f'/kernel/{kernel_id}')
    mock_req_obj.sign.assert_called_once_with()
    mock_req_obj.send.assert_called_once_with()


def test_restart_kernel_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    kernel_id = secrets.token_hex(12)
    with pytest.raises(SornaAPIError):
        restart_kernel(kernel_id)


def test_get_kernel_info_url(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=200)
    mock_req = mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    kernel_id = secrets.token_hex(12)
    get_kernel_info(kernel_id)

    mock_req.assert_called_once_with('GET', f'/kernel/{kernel_id}')
    mock_req_obj.sign.assert_called_once_with()
    mock_req_obj.send.assert_called_once_with()
    mock_req_obj.send.return_value.json.assert_called_once_with()


def test_get_kernel_info_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    kernel_id = secrets.token_hex(12)
    with pytest.raises(SornaAPIError):
        get_kernel_info(kernel_id)


def test_execute_code_url(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=200)
    mock_req = mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    kernel_id = secrets.token_hex(12)
    execute_code(kernel_id, 'hello')

    mock_req.assert_called_once_with('POST', f'/kernel/{kernel_id}',
                                     {'mode': 'query', 'code': 'hello'})
    mock_req_obj.sign.assert_called_once_with()
    mock_req_obj.send.assert_called_once_with()
    mock_req_obj.send.return_value.json.assert_called_once_with()


def test_execute_code_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    kernel_id = secrets.token_hex(12)
    with pytest.raises(SornaAPIError):
        execute_code(kernel_id, 'hello')
