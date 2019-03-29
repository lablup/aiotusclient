from unittest import mock

import asynctest
import pytest

from tests import ContextMagicMock
from ai.backend.client.session import Session


@pytest.mark.asyncio
@pytest.mark.integration
class TestIntegrationManager:

    async def test_get_manager_status(self):
        with Session() as sess:
            resp = sess.Manager.status()
        assert resp['status'] == 'running'
        assert 'active_sessions' in resp


class TestManager:

    def test_status(self, mocker):
        return_value = {'status': 'running', 'active_sessions': 3}
        mock_json_coro = asynctest.CoroutineMock(return_value=return_value)
        mock_req_obj = mocker.Mock()
        mock_req_obj.fetch.return_value = ContextMagicMock(status=200,
                                                           json=mock_json_coro)
        mocker.patch('ai.backend.client.manager.Request', return_value=mock_req_obj)

        with Session() as session:
            resp = session.Manager.status()
            mock_req_obj.fetch.assert_called_once_with()
            assert resp['status'] == return_value['status']
            assert resp['active_sessions'] == return_value['active_sessions']

    def test_freeze(self, mocker):
        mock_req_obj = mocker.Mock()
        mock_req_obj.fetch.return_value = ContextMagicMock(status=204)
        mocker.patch('ai.backend.client.manager.Request', return_value=mock_req_obj)

        with Session() as session:
            session.Manager.freeze()
            mock_req_obj.fetch.assert_called_once_with()

    def test_freeze_opt_force_kill(self, mocker):
        mock_req_obj = mock.Mock()
        mock_req_obj.fetch.return_value = ContextMagicMock(status=204)
        mocker.patch('ai.backend.client.manager.Request', return_value=mock_req_obj)

        with Session() as session:
            session.Manager.freeze(force_kill=True)
            mock_req_obj.fetch.assert_called_once_with()

    def test_unfreeze(self, mocker):
        mock_req_obj = mock.Mock()
        mock_req_obj.fetch.return_value = ContextMagicMock(status=204)
        mocker.patch('ai.backend.client.manager.Request', return_value=mock_req_obj)

        with Session() as session:
            session.Manager.unfreeze()
            mock_req_obj.fetch.assert_called_once_with()
