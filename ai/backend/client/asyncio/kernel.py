import json
from typing import Sequence

import aiohttp
import aiohttp.web

from ..base import AsyncFunctionMixin
from ..exceptions import BackendClientError
from ..request import Request
from ..kernel import BaseKernel

__all__ = (
    'Kernel',
    'AsyncKernel',
    'StreamPty',
)


class Kernel(AsyncFunctionMixin, BaseKernel):

    async def upload(self, files: Sequence[str]):
        rqst = Request('POST', '/kernel/{}/upload'.format(self.kernel_id))
        rqst.content = [
            # name filename file content_type headers
            aiohttp.web.FileField(
                'src', path, open(path, 'rb'), 'application/octet-stream', None
            ) for path in files
        ]
        return (await rqst.asend())

    # only supported in AsyncKernel
    async def stream_pty(self):
        request = Request('GET', '/stream/kernel/{}/pty'.format(self.kernel_id))
        try:
            sess, ws = await request.connect_websocket()
        except aiohttp.ClientResponseError as e:
            raise BackendClientError(e.code, e.message)
        return StreamPty(self.kernel_id, sess, ws)


class StreamPty:

    '''
    A very thin wrapper of aiohttp.WebSocketResponse object.
    It keeps the reference to the mother aiohttp.ClientSession object while the
    connection is alive.
    '''

    def __init__(self, kernel_id, sess, ws):
        self.kernel_id = kernel_id
        self.sess = sess  # we should keep reference while connection is active.
        self.ws = ws

    @property
    def closed(self):
        return self.ws.closed

    def __aiter__(self):
        return self.ws.__aiter__()

    async def __anext__(self):
        msg = await self.ws.__anext__()
        return msg

    def exception(self):
        return self.ws.exception()

    def send_str(self, raw_str):
        self.ws.send_str(raw_str)

    def resize(self, rows, cols):
        self.ws.send_str(json.dumps({
            'type': 'resize',
            'rows': rows,
            'cols': cols,
        }))

    def restart(self):
        self.ws.send_str(json.dumps({
            'type': 'restart',
        }))

    async def close(self):
        await self.ws.close()
        await self.sess.close()


# legacy alias
AsyncKernel = Kernel
