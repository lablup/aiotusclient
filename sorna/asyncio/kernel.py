import json
import sys
import uuid

import aiohttp
from ..exceptions import SornaAPIError
from ..request import Request


async def create_kernel(kernel_type, client_token=None, max_mem=0, timeout=0, return_id_only=True):
    if client_token is not None:
        assert isinstance(client_token, str)
        assert len(client_token) > 8
    request = Request('POST', '/kernel/create', {
        'lang': kernel_type,
        'clientSessionToken': client_token if client_token else uuid.uuid4().hex,
        'resourceLimits': {
            'maxMem': max_mem,
            'timeout': timeout,
        }
    })
    request.sign()
    resp = await request.asend()
    if resp.status == 201:
        if return_id_only:
            return resp.json()['kernelId']
        return resp.json()
    else:
        raise SornaAPIError(resp.status, resp.reason, resp.text())


async def destroy_kernel(kernel_id):
    request = Request('DELETE', '/kernel/{}'.format(kernel_id))
    request.sign()
    resp = await request.asend()
    if resp.status != 204:
        raise SornaAPIError(resp.status, resp.reason, resp.text())


async def restart_kernel(kernel_id):
    request = Request('PATCH', '/kernel/{}'.format(kernel_id))
    request.sign()
    resp = await request.asend()
    if resp.status != 204:
        raise SornaAPIError(resp.status, resp.reason, resp.text())


async def get_kernel_info(kernel_id):
    request = Request('GET', '/kernel/{}'.format(kernel_id))
    request.sign()
    resp = await request.asend()
    if resp.status == 200:
        return resp.json()
    else:
        raise SornaAPIError(resp.status, resp.reason, resp.text())


async def execute_code(kernel_id, code_id, code):
    request = Request('POST', '/kernel/{}'.format(kernel_id), {
        'codeId': code_id,
        'code': code,
    })
    request.sign()
    resp = await request.asend()
    if resp.status == 200:
        return resp.json()['result']
    else:
        raise SornaAPIError(resp.status, resp.reason, resp.text())


class StreamPty:

    def __init__(self, kernel_id, sess, ws):
        self.kernel_id = kernel_id
        self.sess = sess  # we should keep reference while connection is active.
        self.ws = ws

    @property
    def closed(self):
        return self.ws.closed

    if sys.version_info < (3, 5, 2):
        async def __aiter__(self):
            return (await self.ws.__aiter__())
    else:
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


async def stream_pty(kernel_id):
    request = Request('GET', '/stream/kernel/{}/pty'.format(kernel_id))
    request.sign()
    try:
        sess, ws = await request.connect_websocket()
    except aiohttp.errors.HttpProcessingError as e:
        raise SornaAPIError(e.code, e.message)
    return StreamPty(kernel_id, sess, ws)
