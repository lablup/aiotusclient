from abc import abstractmethod
import functools
import inspect
from typing import Iterable, Optional, Sequence
import uuid
import warnings

import aiohttp.web

from .compat import Py36Object
from .exceptions import SornaAPIError, SornaClientError
from .request import Request


class BaseKernel(Py36Object):

    '''
    Implements the request creation and response handling logic,
    while delegating the process of request sending to the subclasses
    via the generator protocol.
    '''

    @abstractmethod
    def _call_base_method(self, meth):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _call_base_clsmethod(cls, meth):
        raise NotImplementedError

    @staticmethod
    def _handle_response(resp, meth_gen):
        if resp.status // 100 != 2:
            raise SornaAPIError(resp.status, resp.reason, resp.text())
        try:
            meth_gen.send(resp)
        except StopIteration as e:
            return e.value
        else:
            raise RuntimeError('Invalid state')

    @classmethod
    def _get_or_create(cls, lang: str,
                       client_token: Optional[str]=None,
                       mounts: Optional[Iterable[str]]=None,
                       max_mem: int=0, exec_timeout: int=0) -> str:
        if client_token:
            assert len(client_token) > 8
        else:
            client_token = uuid.uuid4().hex
        resp = yield Request('POST', '/kernel/create', {
            'lang': lang,
            'clientSessionToken': client_token,
            'limits': {
                'maxMem': max_mem,
                'execTimeout': exec_timeout,
            },
            'mounts': tuple(mounts) if mounts else tuple(),
        })
        return cls(resp.json()['kernelId'])  # type: ignore

    def _destroy(self):
        yield Request('DELETE', '/kernel/{}'.format(self.kernel_id))

    def _restart(self):
        yield Request('PATCH', '/kernel/{}'.format(self.kernel_id))

    def _get_info(self):
        resp = yield Request('GET', '/kernel/{}'.format(self.kernel_id))
        return resp.json()

    def _execute(self, code: str=None, mode: str='query', opts: dict=None):
        if mode == 'query':
            assert code is not None  # but maybe empty due to continuation
            rqst = Request('POST', '/kernel/{}'.format(self.kernel_id), {
                'mode': mode,
                'code': code,
            })
        elif mode == 'batch':
            rqst = Request('POST', '/kernel/{}'.format(self.kernel_id), {
                'mode': mode,
                'code': code,
                'options': {
                    'build': opts.get('build', None),
                    'buildLog': bool(opts.get('buildLog', False)),
                    'exec': opts.get('exec', None),
                },
            })
        elif mode == 'complete':
            rqst = Request('POST', '/kernel/{}'.format(self.kernel_id), {
                'mode': mode,
                'code': code,
                'options': {
                    'row': int(opts.get('row', 0)),
                    'col': int(opts.get('col', 0)),
                    'line': opts.get('line', ''),
                    'post': opts.get('post', ''),
                },
            })
        else:
            raise SornaClientError('Invalid execution mode')
        resp = yield rqst
        return resp.json()['result']

    def __init__(self, kernel_id: str) -> None:
        self.kernel_id = kernel_id
        self.destroy  = self._call_base_method(self._destroy)
        self.restart  = self._call_base_method(self._restart)
        self.get_info = self._call_base_method(self._get_info)
        self.execute  = self._call_base_method(self._execute)

    def __init_subclass__(cls):
        cls.get_or_create = cls._call_base_clsmethod(cls._get_or_create)


class Kernel(BaseKernel):
    '''
    Synchronous request sender kernel using requests.
    '''

    @staticmethod
    def _make_request(gen):
        rqst = next(gen)
        resp = rqst.send()
        return resp

    @classmethod
    def _call_base_clsmethod(cls, meth):
        assert inspect.ismethod(meth)

        @classmethod
        @functools.wraps(meth)
        def _caller(cls, *args, **kwargs):
            gen = meth(*args, **kwargs)
            resp = cls._make_request(gen)
            return cls._handle_response(resp, gen)

        return _caller

    def _call_base_method(self, meth):
        assert inspect.ismethod(meth)

        @functools.wraps(meth)
        def _caller(*args, **kwargs):
            gen = meth(*args, **kwargs)
            resp = self._make_request(gen)
            return self._handle_response(resp, gen)

        return _caller

    def upload(self, files: Sequence[str]):
        rqst = Request('POST', '/kernel/{}/upload'.format(self.kernel_id))
        rqst.content = [
            # name filename file content_type headers
            aiohttp.web.FileField(
                'src', path, open(path, 'rb'), 'application/octet-stream', None
            ) for path in files
        ]
        return rqst.send()


# Legacy functions

def create_kernel(lang: str, client_token: Optional[str]=None,
                  mounts: Optional[Iterable[str]]=None,
                  max_mem: int=0, exec_timeout: int=0,
                  return_id_only: bool=True):
    warnings.warn('deprecated client API', DeprecationWarning, stacklevel=2)
    return Kernel.get_or_create(lang, client_token,
                                mounts, max_mem, exec_timeout)


def destroy_kernel(kernel):
    warnings.warn('deprecated client API', DeprecationWarning, stacklevel=2)
    if isinstance(kernel, Kernel):
        kernel.destroy()
    else:
        Kernel(kernel).destroy()


def restart_kernel(kernel):
    warnings.warn('deprecated client API', DeprecationWarning, stacklevel=2)
    if isinstance(kernel, Kernel):
        kernel.restart()
    else:
        Kernel(kernel).restart()


def get_kernel_info(kernel):
    warnings.warn('deprecated client API', DeprecationWarning, stacklevel=2)
    if isinstance(kernel, Kernel):
        return kernel.get_info()
    else:
        return Kernel(kernel).get_info()


def execute_code(kernel, code: Optional[str]=None,
                 mode: str='query',
                 opts: Optional[str]=None):
    warnings.warn('deprecated client API', DeprecationWarning, stacklevel=2)
    if isinstance(kernel, Kernel):
        return kernel.execute(code, mode, opts)
    else:
        return Kernel(kernel).execute(code, mode, opts)
