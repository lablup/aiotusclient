from ..base import AsyncFunctionMixin
from ..admin import BaseAdmin

__all__ = (
    'Admin',
    'AsyncAdmin',
)


class Admin(AsyncFunctionMixin, BaseAdmin):
    pass


# legacy alias
AsyncAdmin = Admin
