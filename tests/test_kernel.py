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
    mock_json_ftn = lambda: {'kernelId': 'mock_kernel_id'}
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(
        status=201, json=mock_json_ftn
    )
    mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    resp = create_kernel('python')

    assert resp == mock_json_ftn()['kernelId']


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

    destroy_kernel(1)

    mock_req.assert_called_once_with('DELETE', '/kernel/{}'.format(1))
    mock_req_obj.sign.assert_called_once_with()
    mock_req_obj.send.assert_called_once_with()


def test_destroy_kernel_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    with pytest.raises(SornaAPIError):
        destroy_kernel(1)


def test_restart_kernel_url(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=204)
    mock_req = mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    restart_kernel(1)

    mock_req.assert_called_once_with('PATCH', '/kernel/{}'.format(1))
    mock_req_obj.sign.assert_called_once_with()
    mock_req_obj.send.assert_called_once_with()


def test_restart_kernel_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    with pytest.raises(SornaAPIError):
        restart_kernel(1)


def test_get_kernel_info_url(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=200)
    mock_req = mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    get_kernel_info(1)

    mock_req.assert_called_once_with('GET', '/kernel/{}'.format(1))
    mock_req_obj.sign.assert_called_once_with()
    mock_req_obj.send.assert_called_once_with()
    mock_req_obj.send.return_value.json.assert_called_once_with()


def test_get_kernel_info_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    with pytest.raises(SornaAPIError):
        get_kernel_info(1)


def test_execute_code_url(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=200)
    mock_req = mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    execute_code(1, 2, 'hello')

    mock_req.assert_called_once_with('POST', '/kernel/{}'.format(1),
                                     {'codeId': 2, 'code': 'hello'})
    mock_req_obj.sign.assert_called_once_with()
    mock_req_obj.send.assert_called_once_with()
    mock_req_obj.send.return_value.json.assert_called_once_with()


def test_execute_code_raises_err_with_abnormal_status(mocker):
    mock_req_obj = mock.Mock()
    mock_req_obj.send.return_value = mock.MagicMock(status=400)
    mocker.patch('sorna.kernel.Request', return_value=mock_req_obj)

    with pytest.raises(SornaAPIError):
        execute_code(1, 2, 'hello')
