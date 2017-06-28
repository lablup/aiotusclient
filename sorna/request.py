from collections import OrderedDict
from datetime import datetime
from typing import Any, Mapping, Optional, Sequence, Union
from urllib.parse import urljoin

import aiohttp
import aiohttp.web
from async_timeout import timeout as _timeout
from dateutil.tz import tzutc
from multidict import CIMultiDict
import requests
import simplejson as json

from .auth import generate_signature
from .config import APIConfig, get_config
from .exceptions import SornaAPIError


class Request:

    __slots__ = ['config', 'method', 'path',
                 'date', 'headers',
                 'content_type', '_content']

    _allowed_methods = frozenset([
        'GET', 'HEAD', 'POST',
        'PUT', 'PATCH', 'DELETE',
        'OPTIONS'])

    def __init__(self, method: str='GET',
                 path: Optional[str]=None,
                 content: Optional[Mapping]=None,
                 config: Optional[APIConfig]=None) -> None:
        self.config = config if config else get_config()
        self.method = method
        if path.startswith('/'):
            path = path[1:]
        self.path = path
        self.date = datetime.now(tzutc())
        self.headers = CIMultiDict([
            ('Date', self.date.isoformat()),
            ('X-Sorna-Version', self.config.version),
        ])
        self.content = content if content is not None else b''

    @property
    def content(self) -> Union[bytes, bytearray, None]:
        '''
        Retrieves the content in the original form.
        Private codes should NOT use this as it incurs duplicate
        encoding/decoding.
        '''
        if self._content is None:
            raise ValueError('content is not set.')
        if self.content_type == 'application/octet-stream':
            return self._content
        elif self.content_type == 'application/json':
            return json.loads(self._content.decode('utf-8'))
        elif self.content_type == 'text/plain':
            return self._content.decode('utf-8')
        elif self.content_type == 'multipart/form-data':
            return self._content
        else:
            raise RuntimeError('should not reach here')  # pragma: no cover

    @content.setter
    def content(self, value: Union[bytes, bytearray,
                                   Mapping[str, Any],
                                   Sequence[aiohttp.web.FileField],
                                   None]):
        '''
        Sets the content of the request.
        Depending on the type of content, it automatically sets appropriate
        headers such as content-type and content-length.
        '''
        if isinstance(value, (bytes, bytearray)):
            self.content_type = 'application/octet-stream'
            self._content = value
            self.headers['Content-Type'] = self.content_type
            self.headers['Content-Length'] = str(len(self._content))
        elif isinstance(value, str):
            self.content_type = 'text/plain'
            self._content = value.encode('utf-8')
            self.headers['Content-Type'] = self.content_type
            self.headers['Content-Length'] = str(len(self._content))
        elif isinstance(value, (dict, OrderedDict)):
            self.content_type = 'application/json'
            self._content = json.dumps(value).encode('utf-8')
            self.headers['Content-Type'] = self.content_type
            self.headers['Content-Length'] = str(len(self._content))
        elif isinstance(value, (list, tuple)):
            self.content_type = 'multipart/form-data'
            self._content = value
            # Let the http client library decide the header values.
            # (e.g., message boundaries)
            if 'Content-Length' in self.headers:
                del self.headers['Content-Length']
            if 'Content-Type' in self.headers:
                del self.headers['Content-Type']
        else:
            raise TypeError('Unsupported content value type.')

    def _sign(self, access_key=None, secret_key=None, hash_type=None):
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
            self.date, self.path, self.content_type, self._content,
            access_key, secret_key, hash_type)
        self.headers.update(hdrs)

    def build_url(self):
        major_ver = self.config.version.split('.', 1)[0]
        path = '/' + self.path if len(self.path) > 0 else ''
        return urljoin(self.config.endpoint, major_ver + path)

    # TODO: attach rate-limit information

    def send(self, *, sess=None):
        '''
        Sends the request to the server.
        '''
        assert self.method in self._allowed_methods
        if sess is None:
            sess = requests.Session()
        else:
            assert isinstance(sess, requests.Session)
        self._sign()
        reqfunc = getattr(sess, self.method.lower())
        if self.content_type == 'multipart/form-data':
            files = map(lambda f: (f.name,
                                   (f.filename, f.file, f.content_type)
                                  ),
                        self._content)
            resp = reqfunc(self.build_url(),
                           files=files,
                           headers=self.headers)
        else:
            resp = reqfunc(self.build_url(),
                           data=self._content,
                           headers=self.headers)
        try:
            return Response(resp.status_code, resp.reason, resp.text,
                            resp.headers['content-type'],
                            resp.headers['content-length'])
        except requests.exceptions.RequestException as e:
            raise SornaAPIError from e

    async def asend(self, *, sess=None, timeout=10.0):
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
            if self.content_type == 'multipart/form-data':
                with aiohttp.MultipartWriter('mixed') as mpwriter:
                    for file in self._content:
                        part = mpwriter.append(file.file)
                        part.set_content_disposition('attachment',
                                                     filename=file.filename)
                data = mpwriter
            else:
                data = self._content
            self._sign()
            reqfunc = getattr(sess, self.method.lower())
            try:
                with _timeout(timeout):
                    resp = await reqfunc(self.build_url(),
                                         data=data,
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
