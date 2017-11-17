import os
from pathlib import Path
import re

import aiohttp

from .base import BaseFunction, SyncFunctionMixin
from .request import Request

__all__ = (
    'BaseVFolder',
    'VFolder',
)

_rx_slug = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$')


class BaseVFolder(BaseFunction):
    @classmethod
    def _create(cls, name: str):
        assert _rx_slug.search(name) is not None
        resp = yield Request('POST', '/folders/', {
            'name': name,
        })
        return resp.json()

    @classmethod
    def _list(cls):
        resp = yield Request('GET', '/folders/')
        return resp.json()

    @classmethod
    def _get(cls, name: str):
        return cls(name)

    def _info(self):
        resp = yield Request('GET', '/folders/{0}'.format(self.name))
        return resp.json()

    def _delete(self):
        resp = yield Request('DELETE', '/folders/{0}'.format(self.name))
        if resp.status == 200:
            return resp.json()

    def __init__(self, name: str):
        assert _rx_slug.search(name) is not None
        self.name = name
        self.delete = self._call_base_method(self._delete)
        self.info = self._call_base_method(self._info)

    def __init_subclass__(cls):
        cls.create = cls._call_base_clsmethod(cls._create)
        cls.list = cls._call_base_clsmethod(cls._list)
        cls.get = cls._call_base_clsmethod(cls._get)


class VFolder(SyncFunctionMixin, BaseVFolder):

    def upload(self, filename):
        rqst = Request('POST', '/folders/{0}/upload'.format(self.name))
        rel_path = Path(filename).resolve().relative_to(Path(os.getcwd()).resolve())
        rqst.content = [
            # name filename file content_type headers
            aiohttp.web.FileField(
                'src', str(rel_path), open(rel_path, 'rb'),
                'application/octet-stream', None
            )
        ]
        return rqst.send()
