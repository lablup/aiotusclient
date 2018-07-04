from aioresponses import aioresponses
import pytest

from ai.backend.client.base import BaseFunction, SyncFunctionMixin
from ai.backend.client.exceptions import BackendAPIError
from ai.backend.client.request import Request
from ai.backend.client.session import Session


class DummyFunction(SyncFunctionMixin, BaseFunction):

    _session = None

    def _do_this(self):
        rqst = Request(self._session, 'POST', 'function')
        resp = yield rqst
        return resp

    def __init__(self, *, config=None):
        self.config = config
        self.do_this = self._call_base_method(self._do_this)


def test_server_error(defconfig, dummy_endpoint):
    func = DummyFunction(config=defconfig)

    with Session() as session:
        DummyFunction._session = session

        with aioresponses() as m:
            m.post(dummy_endpoint + 'function', status=500, body=b'Ooops!')
            with pytest.raises(BackendAPIError) as exc_info:
                func.do_this()
            assert exc_info.value.data['type'] == \
                   'https://api.backend.ai/probs/generic-error'

        with aioresponses() as m:
            m.post(dummy_endpoint + 'function', status=500, payload={
                'type': 'https://api.backend.ai/probs/internal-server-error',
                'title': 'Internal Server Error',
            })
            with pytest.raises(BackendAPIError) as exc_info:
                func.do_this()
            assert exc_info.value.data['type'] == \
                   'https://api.backend.ai/probs/internal-server-error'
