from collections import OrderedDict
from datetime import datetime
from typing import Mapping, Optional, Union
from urllib.parse import urljoin

import aiohttp
from async_timeout import timeout as _timeout
from dateutil.tz import tzutc
import requests
import simplejson as json

from .auth import generate_signature
from .config import APIConfig, get_config
from .exceptions import SornaAPIError


class Request:

    __slots__ = ['config', 'method', 'path',
                 'data', 'date', 'headers',
                 '_content']

    _allowed_methods = frozenset([
        'GET', 'HEAD', 'POST',
        'PUT', 'PATCH', 'DELETE',
        'OPTIONS'])

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
            self.headers['Content-Length'] = str(len(self._content))
        return self._content

    @content.setter
    def content(self, value: Union[bytes, bytearray, None]):
        '''
        Manually set the raw bytes content of the request body.
        It raises AssertionError if the request already has a value in the `data` field.
        '''
        if value is not None:
            assert not self.data, 'request.data should be empty to set request.content manually.'
            self.headers['Content-Length'] = str(len(value))
        self._content = value

    def sign(self, access_key=None, secret_key=None, hash_type=None):
        '''
        Calculates the signature of the given request and adds the
        Authorization HTTP header.
        It should be called at the very end of request preparation and before
        sending the request to the server.
        '''
        if access_key is None:
            access_key = self.config.access_key
        if secret_key is None:
            secret_key = self.config.secret_key
        if hash_type is None:
            hash_type = self.config.hash_type
        hdrs, _ = generate_signature(
            self.method, self.config.version, self.config.endpoint,
            self.date, self.path, self.content,
            access_key, secret_key, hash_type)
        self.headers.update(hdrs)

    def build_url(self):
        major_ver = self.config.version.split('.', 1)[0]
        path = '/' + self.path if len(self.path) > 0 else ''
        return urljoin(self.config.endpoint, major_ver + path)

    # TODO: attach rate-limit information

    def send(self, sess=None):
        '''
        Sends the request to the server.
        '''
        assert self.method in self._allowed_methods
        if sess is None:
            sess = requests.Session()
        else:
            assert isinstance(sess, requests.Session)
        reqfunc = getattr(sess, self.method.lower())
        resp = reqfunc(self.build_url(),
                       data=self.content,
                       headers=self.headers)
        try:
            return Response(resp.status_code, resp.reason, resp.text,
                            resp.headers['content-type'],
                            resp.headers['content-length'])
        except requests.exceptions.RequestException as e:
            raise SornaAPIError from e

    async def asend(self, sess=None, timeout=10.0):
        '''
        Sends the request to the server.

        This method is a coroutine.
        '''
        assert self.method in self._allowed_methods
        if sess is None:
            sess = aiohttp.ClientSession()
        else:
            assert isinstance(sess, aiohttp.ClientSession)
        with sess:
            reqfunc = getattr(sess, self.method.lower())
            try:
                with _timeout(timeout):
                    resp = await reqfunc(self.build_url(),
                                         data=self.content,
                                         headers=self.headers)
                    async with resp:
                        body = await resp.text()
                        return Response(resp.status, resp.reason, body,
                                        resp.content_type,
                                        len(body))
            except Exception as e:
                raise SornaAPIError from e

    async def connect_websocket(self, sess=None):
        '''
        Creates a WebSocket connection.

        This method is an async-generator, where you can fetch WebSocket
        messages using `async for` clause to the returned value.
        '''
        assert self.method == 'GET'
        if sess is None:
            sess = aiohttp.ClientSession()
        else:
            assert isinstance(sess, aiohttp.ClientSession)
        ws = await sess.ws_connect(self.build_url(), headers=self.headers)
        return sess, ws


class Response:

    __slots__ = ['_status', '_reason',
                 '_content_type', '_content_length',
                 '_body']

    def __init__(self, status, reason, body,
                 content_type='text/plain',
                 content_length=None):
        self._status = status
        self._reason = reason
        self._body = body
        self._content_type = content_type
        self._content_length = content_length

        # TODO: include rate-limiting information from headers

    @property
    def status(self):
        return self._status

    @property
    def reason(self):
        return self._reason

    @property
    def content_type(self):
        return self._content_type

    @property
    def content_length(self):
        return self._content_length

    def text(self):
        return self._body

    def json(self):
        return json.loads(self._body)
