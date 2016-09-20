from collections import OrderedDict
from datetime import datetime
from typing import Mapping, Optional, Union

from dateutil.tz import tzutc
import simplejson as json

from .config import APIConfig, get_config


class Request:

    __slots__ = ['config', 'method', 'path', 'data', 'date', 'headers', '_body']

    def __init__(self, method: str='GET',
                 path: Optional[str]=None,
                 data: Optional[Mapping]=None,
                 config: Optional[APIConfig]=None):
        self.config = config if config else get_config()
        self.method = method
        self.path = path
        self.data = data if data else OrderedDict()
        self.date = datetime.now(tzutc())
        self.headers = OrderedDict([
            ('Content-Type', 'application/json'),
            ('Date', self.date.isoformat()),
            ('X-Sorna-Version', self.config.version),
        ])
        self._body = None

    @property
    def body(self) -> Union[bytes, bytearray, None]:
        '''
        Retrieves the JSON-encoded body content from request.data object.
        Once called, the result is cached until request.body is set manually.
        After reading this, you need to manually reset it by setting to None
        if you have further content changes of request.data.
        '''
        if self._body is None:
            if not self.data:  # for empty data
                self._body = b''
            else:
                self._body = json.dumps(self.data, ensure_ascii=False).encode()
            self.headers['Content-Length'] = len(self._body)
        return self._body

    @body.setter
    def body(self, value: Union[bytes, bytearray, None]):
        '''
        Manually set the raw bytes content of the request body.
        It raises AssertionError if the request already has a value in the `data` field.
        '''
        if value is not None:
            assert not self.data, 'request.data should be empty to set request.body manually.'
            self.headers['Content-Length'] = len(value)
        self._body = value
