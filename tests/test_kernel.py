from unittest import mock

import pytest

from ai.backend.client.exceptions import BackendAPIError
from ai.backend.client.compat import token_hex
from ai.backend.client.config import APIConfig
from ai.backend.client.kernel import Kernel


def test_create_with_config(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mocker.MagicMock(status=201,
                                                      json=mock.MagicMock())
    mock_req = mocker.patch('ai.backend.client.kernel.Request',
                            return_value=mock_req_obj)

    myconfig = APIConfig(
        endpoint='https://localhost:9999',
        access_key='1234',
        secret_key='asdf',
    )
    k = Kernel.get_or_create('python', config=myconfig)
    mock_req.assert_called_once_with('POST', '/kernel/create', mocker.ANY,
                                     config=myconfig)
    assert k.config.endpoint == 'https://localhost:9999'
    assert k.config.access_key == '1234'
    assert k.config.secret_key == 'asdf'


def test_create_kernel_url(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mocker.MagicMock(status=201,
                                                      json=mock.MagicMock())
    mock_req = mocker.patch('ai.backend.client.kernel.Request',
                            return_value=mock_req_obj)

    Kernel.get_or_create('python')

    mock_req.assert_called_once_with('POST', '/kernel/create', mocker.ANY,
                                     config=None)
    mock_req_obj.send.assert_called_once_with()
    mock_req_obj.send.return_value.json.assert_called_once_with()


def test_create_kernel_return_id_only(mocker):
    mock_json_func = lambda: {'kernelId': 'mock_kernel_id'}
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(
        status=201, json=mock_json_func
    )
    mocker.patch('ai.backend.client.kernel.Request', return_value=mock_req_obj)

    k = Kernel.get_or_create('python')

    assert k.kernel_id == mock_json_func()['kernelId']


def test_create_kernel_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('ai.backend.client.kernel.Request', return_value=mock_req_obj)

    with pytest.raises(BackendAPIError):
        Kernel.get_or_create('python')


def test_destroy_kernel_url(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=204)
    mock_req = mocker.patch('ai.backend.client.kernel.Request',
                            return_value=mock_req_obj)

    kernel_id = token_hex(12)
    k = Kernel(kernel_id)
    k.destroy()

    mock_req.assert_called_once_with('DELETE', '/kernel/{}'.format(kernel_id),
                                     config=None)
    mock_req_obj.send.assert_called_once_with()


def test_destroy_kernel_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('ai.backend.client.kernel.Request', return_value=mock_req_obj)

    kernel_id = token_hex(12)
    with pytest.raises(BackendAPIError):
        k = Kernel(kernel_id)
        k.destroy()


def test_restart_kernel_url(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=204)
    mock_req = mocker.patch('ai.backend.client.kernel.Request',
                            return_value=mock_req_obj)

    kernel_id = token_hex(12)
    k = Kernel(kernel_id)
    k.restart()

    mock_req.assert_called_once_with('PATCH', '/kernel/{}'.format(kernel_id),
                                     config=None)
    mock_req_obj.send.assert_called_once_with()


def test_restart_kernel_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('ai.backend.client.kernel.Request', return_value=mock_req_obj)

    kernel_id = token_hex(12)
    with pytest.raises(BackendAPIError):
        k = Kernel(kernel_id)
        k.restart()


def test_get_kernel_info_url(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=200)
    mock_req = mocker.patch('ai.backend.client.kernel.Request',
                            return_value=mock_req_obj)

    kernel_id = token_hex(12)
    k = Kernel(kernel_id)
    k.get_info()

    mock_req.assert_called_once_with('GET', '/kernel/{}'.format(kernel_id),
                                     config=None)
    mock_req_obj.send.assert_called_once_with()
    mock_req_obj.send.return_value.json.assert_called_once_with()


def test_get_kernel_info_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('ai.backend.client.kernel.Request', return_value=mock_req_obj)

    kernel_id = token_hex(12)
    with pytest.raises(BackendAPIError):
        k = Kernel(kernel_id)
        k.get_info()


def test_execute_code_url(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=200)
    mock_req = mocker.patch('ai.backend.client.kernel.Request',
                            return_value=mock_req_obj)

    kernel_id = token_hex(12)
    k = Kernel(kernel_id)
    run_id = token_hex(8)
    k.execute(run_id, 'hello')

    mock_req.assert_called_once_with(
        'POST', '/kernel/{}'.format(kernel_id),
        {'mode': 'query', 'runId': run_id, 'code': 'hello'},
        config=None)
    mock_req_obj.send.assert_called_once_with()
    mock_req_obj.send.return_value.json.assert_called_once_with()


def test_execute_code_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('ai.backend.client.kernel.Request', return_value=mock_req_obj)

    kernel_id = token_hex(12)
    run_id = token_hex(8)
    with pytest.raises(BackendAPIError):
        k = Kernel(kernel_id)
        k.execute(run_id, 'hello')
