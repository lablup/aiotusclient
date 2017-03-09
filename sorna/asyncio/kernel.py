import functools
import inspect
import json
import sys
from typing import Iterable, Optional
import uuid
import warnings

import aiohttp
from ..exceptions import SornaAPIError, SornaClientError
from ..request import Request
from ..kernel import BaseKernel


class AsyncKernel(BaseKernel):
    '''
    Asynchronous request sender kernel using aiohttp.
    '''

    @staticmethod
    async def _make_request(gen):
        rqst = next(gen)
        rqst.sign()
        resp = await rqst.asend()
        return resp

    @classmethod
    def _call_base_clsmethod(cls, meth):
        assert inspect.ismethod(meth)
        @classmethod
        @functools.wraps(meth)
        async def _caller(cls, *args, **kwargs):
            gen = meth(*args, **kwargs)
            resp = await cls._make_request(gen)
            return cls._handle_response(resp, gen)
        return _caller

    def _call_base_method(self, meth):
        assert inspect.ismethod(meth)
        @functools.wraps(meth)
        async def _caller(*args, **kwargs):
            gen = meth(*args, **kwargs)
            resp = await self._make_request(gen)
            return self._handle_response(resp, gen)
        return _caller

    # only supported in AsyncKernel
    async def stream_pty(self):
        request = Request('GET', '/stream/kernel/{}/pty'.format(self.kernel_id))
        request.sign()
        try:
            sess, ws = await request.connect_websocket()
        except aiohttp.errors.HttpProcessingError as e:
            raise SornaClientError(e.code, e.message)
        return StreamPty(self.kernel_id, sess, ws)


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


# Legacy functions

async def create_kernel(lang: str, client_token: Optional[str]=None,
                        mounts: Optional[Iterable[str]]=None,
                        max_mem: int=0, exec_timeout: int=0,
                        return_id_only: bool=True):
    warnings.warn('deprecated client API', DeprecationWarning, stacklevel=2)
    return await AsyncKernel.get_or_create(lang, client_token,
                                           mounts, max_mem, exec_timeout)


async def destroy_kernel(kernel):
    warnings.warn('deprecated client API', DeprecationWarning, stacklevel=2)
    if isinstance(kernel, AsyncKernel):
        await kernel.destroy()
    elif isinstance(kernel, str):
        await AsyncKernel(kernel).destroy()
    else:
        raise SornaClientError('Called async API with synchronous Kernel object')


async def restart_kernel(kernel):
    warnings.warn('deprecated client API', DeprecationWarning, stacklevel=2)
    if isinstance(kernel, AsyncKernel):
        await kernel.restart()
    elif isinstance(kernel, str):
        await AsyncKernel(kernel).restart()
    else:
        raise SornaClientError('Called async API with synchronous Kernel object')


async def get_kernel_info(kernel):
    warnings.warn('deprecated client API', DeprecationWarning, stacklevel=2)
    if isinstance(kernel, AsyncKernel):
        return await kernel.get_info()
    elif isinstance(kernel, str):
        return await AsyncKernel(kernel).get_info()
    else:
        raise SornaClientError('Called async API with synchronous Kernel object')


async def execute_code(kernel, code: Optional[str]=None,
                       mode: str='query',
                       opts: Optional[str]=None):
    warnings.warn('deprecated client API', DeprecationWarning, stacklevel=2)
    if isinstance(kernel, AsyncKernel):
        return await kernel.execute(code, mode, opts)
    elif isinstance(kernel, str):
        return await AsyncKernel(kernel).execute(code, mode, opts)
    else:
        raise SornaClientError('Called async API with synchronous Kernel object')


async def stream_pty(kernel):
    warnings.warn('deprecated client API', DeprecationWarning, stacklevel=2)
    if isinstance(kernel, AsyncKernel):
        return await kernel.stream_pty()
    elif isinstance(kernel, str):
        return await AsyncKernel(kernel).stream_pty()
    else:
        raise SornaClientError('Called async API with synchronous Kernel object')
