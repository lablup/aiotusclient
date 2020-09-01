import asyncio
import base64
from typing import Optional

import aiohttp

from .exceptions import TusUploadFailed


class BaseTusRequest:
    """
    Http Request Abstraction.

    Sets up tus custom http request on instantiation.

    requires argument 'uploader' an instance of tusclient.uploader.Uploader
    on instantiation.

    :Attributes:
        - response_headers (dict)
        - file (file):
            The file that is being uploaded.
    """

    def __init__(self, uploader):
        self._url = uploader.url
        self.response_headers = {}
        self.status_code = None
        self.response_content = None
        self.file = uploader.get_file_stream()
        self.file.seek(uploader.offset)

        self._request_headers = {
            'upload-offset': str(uploader.offset),
            'Content-Type': 'application/offset+octet-stream'
        }
        self._request_headers.update(uploader.get_headers())
        self._content_length = uploader.get_request_length()
        self._upload_checksum = uploader.upload_checksum
        self._checksum_algorithm = uploader.checksum_algorithm
        self._checksum_algorithm_name = uploader.checksum_algorithm_name

    def add_checksum(self, chunk: bytes):
        if self._upload_checksum:
            self._request_headers['upload-checksum'] = \
                ' '.join((
                    self._checksum_algorithm_name,
                    base64.b64encode(
                        self._checksum_algorithm(chunk).digest()
                    ).decode('ascii'),
                ))


class AsyncTusRequest(BaseTusRequest):
    """Class to handle async Tus upload requests"""
    def __init__(self, *args, io_loop: Optional[asyncio.AbstractEventLoop] = None, **kwargs):
        self.io_loop = io_loop
        super().__init__(*args, **kwargs)

    async def perform(self):
        """
        Perform actual request.
        """

        chunk = self.file.read(self._content_length)
        self.add_checksum(chunk)
        try:
            async with aiohttp.ClientSession(loop=self.io_loop) as session:
                async with session.patch(self._url, data=chunk,
                                         headers=self._request_headers) as resp:
                    self.status_code = resp.status
                    self.response_headers = {
                        k.lower(): v for k, v in resp.headers.items()}
                    self.response_content = await resp.content.read()
        except aiohttp.ClientError as error:
            raise TusUploadFailed(error)
