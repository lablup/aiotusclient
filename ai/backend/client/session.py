import asyncio
import threading
import queue

import aiohttp

from .base import SyncFunctionMixin, AsyncFunctionMixin


__all__ = (
    'BaseSession',
    'Session',
    'AsyncSession',
)


class _SyncWorkerThread(threading.Thread):

    sentinel = object()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.work_queue = queue.Queue()
        self.done_queue = queue.Queue()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            while True:
                coro = self.work_queue.get()
                if coro is self.sentinel:
                    break
                try:
                    result = loop.run_until_complete(coro)
                except Exception as e:
                    self.done_queue.put_nowait(e)
                else:
                    self.done_queue.put_nowait(result)
                self.work_queue.task_done()
        except (SystemExit, KeyboardInterrupt):
            pass
        finally:
            loop.close()

    def execute(self, coro):
        self.work_queue.put(coro)
        result = self.done_queue.get()
        self.done_queue.task_done()
        if isinstance(result, Exception):
            raise result
        return result


class BaseSession:
    __slots__ = (
        'closed',
        'aiohttp_session',
        'Admin', 'Agent', 'Kernel', 'KeyPair', 'VFolder',
    )


class Session(BaseSession):

    __slots__ = BaseSession.__slots__ + (
        'worker_thread',
    )

    def __init__(self):
        self.closed = False
        self.worker_thread = _SyncWorkerThread()
        self.worker_thread.start()

        async def _create_aiohttp_session():
            return aiohttp.ClientSession()

        self.aiohttp_session = self.worker_thread.execute(_create_aiohttp_session())

        from .admin import BaseAdmin
        from .agent import BaseAgent
        from .kernel import BaseKernel
        from .keypair import BaseKeyPair
        from .vfolder import BaseVFolder
        self.Admin = type('Admin', (SyncFunctionMixin, BaseAdmin), {
            '_session': self,
        })
        self.Agent = type('Agent', (SyncFunctionMixin, BaseAgent), {
            '_session': self,
        })
        self.Kernel = type('Kernel', (SyncFunctionMixin, BaseKernel), {
            '_session': self,
        })
        self.KeyPair = type('KeyPair', (SyncFunctionMixin, BaseKeyPair), {
            '_session': self,
        })
        self.VFolder = type('VFolder', (SyncFunctionMixin, BaseVFolder), {
            '_session': self,
        })

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.worker_thread.work_queue.put(self.aiohttp_session.close())
        self.worker_thread.work_queue.put(self.worker_thread.sentinel)
        self.worker_thread.join()

    def __enter__(self):
        assert not self.closed, 'Cannot reuse closed session'
        return self

    def __exit__(self, exc_type, exc_obj, exc_tb):
        self.close()


class AsyncSession(BaseSession):

    __slots__ = BaseSession.__slots__ + ()

    def __init__(self):
        self.closed = False
        self.aiohttp_session = aiohttp.ClientSession()

        from .admin import BaseAdmin
        from .agent import BaseAgent
        from .kernel import BaseKernel
        from .keypair import BaseKeyPair
        from .vfolder import BaseVFolder
        self.Admin = type('Admin', (AsyncFunctionMixin, BaseAdmin), {
            '_session': self,
        })
        self.Agent = type('Agent', (AsyncFunctionMixin, BaseAgent), {
            '_session': self,
        })
        self.Kernel = type('Kernel', (AsyncFunctionMixin, BaseKernel), {
            '_session': self,
        })
        self.KeyPair = type('KeyPair', (AsyncFunctionMixin, BaseKeyPair), {
            '_session': self,
        })
        self.VFolder = type('VFolder', (AsyncFunctionMixin, BaseVFolder), {
            '_session': self,
        })

    async def close(self):
        if self.closed:
            return
        self.closed = True
        await self.aiohttp_session.close()

    async def __aenter__(self):
        assert not self.closed, 'Cannot reuse closed session'
        return self

    async def __aexit__(self, exc_type, exc_obj, exc_tb):
        await self.close()
