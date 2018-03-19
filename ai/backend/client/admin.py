from typing import Any, Mapping, Optional

from .base import BaseFunction, SyncFunctionMixin
from .config import APIConfig
from .request import Request

__all__ = (
    'BaseAdmin',
    'Admin',
)


class BaseAdmin(BaseFunction):

    @classmethod
    def _query(cls, query: str,
               variables: Optional[Mapping[str, Any]]=None,
               config: APIConfig=None):
        gql_query = {
            'query': query,
            'variables': variables if variables else {},
        }
        resp = yield Request('POST', '/admin/graphql', gql_query, config=config)
        return resp.json()

    def __init_subclass__(cls):
        cls.query = cls._call_base_clsmethod(cls._query)


class Admin(SyncFunctionMixin, BaseAdmin):
    pass
