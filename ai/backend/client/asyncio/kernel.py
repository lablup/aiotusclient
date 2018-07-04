from ..base import AsyncFunctionMixin
from ..kernel import BaseKernel

__all__ = (
    'Kernel',
    'AsyncKernel',
)


class Kernel(AsyncFunctionMixin, BaseKernel):
    '''
    Deprecated! Use ai.backend.client.AsyncSession instead.
    '''
    pass


# legacy alias
AsyncKernel = Kernel
