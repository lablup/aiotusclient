import asyncio
from collections import OrderedDict
from datetime import datetime
from typing import Mapping, Optional, Union
from urllib.parse import urljoin

import aiohttp
from async_timeout import timeout as _timeout
from dateutil.tz import tzutc
import requests
import simplejson as json

from .config import APIConfig, get_config

_shared_sess = None


class Request:

    __slots__ = ['config', 'method', 'path', 'data', 'date', 'headers', '_content']

    _allowed_methods = frozenset(['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])

    def __init__(self, method: str='GET',
                 path: Optional[str]=None,
                 data: Optional[Mapping]=None,
                 config: Optional[APIConfig]=None):
        self.config = config if config else get_config()
        self.method = method
        if path.startswith('/'):
            path = path[1:]
        self.path = path
        self.data = data if data else OrderedDict()
        self.date = datetime.now(tzutc())
        self.headers = OrderedDict([
            ('Content-Type', 'application/json'),
            ('Date', self.date.isoformat()),
            ('X-Sorna-Version', self.config.version),
        ])
        self._content = None

    @property
    def content(self) -> Union[bytes, bytearray, None]:
        '''
        Retrieves the JSON-encoded body content from request.data object.
        Once called, the result is cached until request.content is set manually.
        After reading this, you need to manually reset it by setting to None
        if you have further content changes of request.data.
        '''
        if self._content is None:
            if not self.data:  # for empty data
                self._content = b''
            else:
                self._content = json.dumps(self.data, ensure_ascii=False).encode()
            self.headers['Content-Length'] = len(self._content)
        return self._content

    @content.setter
    def content(self, value: Union[bytes, bytearray, None]):
        '''
        Manually set the raw bytes content of the request body.
        It raises AssertionError if the request already has a value in the `data` field.
        '''
        if value is not None:
            assert not self.data, 'request.data should be empty to set request.content manually.'
            self.headers['Content-Length'] = len(value)
        self._content = value

    def json(self):
        return json.loads(self._content)

    def text(self):
        if self._content is None:
            return None
        return self._content.decode()

    def build_url(self):
        major_ver = self.config.version.split('.', 1)[0]
        path = '/' + self.path if len(self.path) > 0 else ''
        return urljoin(self.config.endpoint, major_ver + path)

    def send(self):
        '''
        Sends the request to the server.
        '''
        assert self.method in self._allowed_methods
        reqfunc = getattr(requests, self.method.lower())
        resp = reqfunc(self.build_url(), json=self.data)
        return Response(resp.text)

    async def asend(self, sess=None, timeout=10.0):
        '''
        Sends the request to the server.

        This method is a coroutine.
        '''
        global _shared_sess
        if not sess:
            if not _shared_sess:
                sess = aiohttp.ClientSession()
                _shared_sess = sess
            else:
                sess = _shared_sess
        reqfunc = getattr(sess, self.method.lower())
        with _timeout(timeout):
            async with reqfunc(self.build_url()) as resp:
                body = await resp.text()
        return Response(body)


class Response:

    def __init__(self, body):
        self._body = body

    def text(self):
        return self._body

    def json(self):
        return json.loads(self._body)
