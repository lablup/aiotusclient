from ..base import AsyncFunctionMixin
from ..vfolder import BaseVFolder

__all__ = (
    'VFolder',
)


class VFolder(AsyncFunctionMixin, BaseVFolder):
    '''
    Deprecated! Use ai.backend.client.AsyncSession instead.
    '''
    pass
