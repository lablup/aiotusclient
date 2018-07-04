from ..base import AsyncFunctionMixin
from ..admin import BaseAdmin

__all__ = (
    'Admin',
    'AsyncAdmin',
)


class Admin(AsyncFunctionMixin, BaseAdmin):
    '''
    Deprecated! Use ai.backend.client.AsyncSession instead.
    '''
    pass


# legacy alias
AsyncAdmin = Admin
