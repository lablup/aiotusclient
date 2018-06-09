import asyncio
from datetime import datetime
from pathlib import Path
import re
from typing import Sequence, Union

import aiohttp
from async_timeout import timeout as _timeout
from dateutil.tz import tzutc
from tqdm import tqdm

from .base import BaseFunction, SyncFunctionMixin
from .config import APIConfig
from .exceptions import BackendClientError
from .request import Request
from .cli.pretty import ProgressReportingReader

__all__ = (
    'BaseVFolder',
    'VFolder',
)

_rx_slug = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$')


class BaseVFolder(BaseFunction):
    @classmethod
    def _create(cls, name: str, *,
                config: APIConfig=None):
        assert _rx_slug.search(name) is not None
        resp = yield Request('POST', '/folders/', {
            'name': name,
        }, config=config)
        return resp.json()

    @classmethod
    def _list(cls, *, config: APIConfig=None):
        resp = yield Request('GET', '/folders/', config=config)
        return resp.json()

    @classmethod
    def _get(cls, name: str, *, config: APIConfig=None):
        return cls(name, config=config)

    def _info(self):
        resp = yield Request('GET', '/folders/{0}'.format(self.name),
                             config=self.config)
        return resp.json()

    def _delete(self):
        resp = yield Request('DELETE', '/folders/{0}'.format(self.name),
                             config=self.config)
        if resp.status == 200:
            return resp.json()

    def _upload(self, files: Sequence[Union[str, Path]],
               basedir: Union[str, Path]=None,
               show_progress: bool=False):
        fields = []
        base_path = (Path.cwd() if basedir is None
                     else Path(basedir).resolve())
        files = [Path(file).resolve() for file in files]
        total_size = 0
        for file_path in files:
            total_size += file_path.stat().st_size
        tqdm_obj = tqdm(desc='Uploading files',
                        unit='bytes', unit_scale=True,
                        total=total_size,
                        disable=not show_progress)
        with tqdm_obj:
            for file_path in files:
                try:
                    fields.append(aiohttp.web.FileField(
                        'src',
                        str(file_path.relative_to(base_path)),
                        ProgressReportingReader(str(file_path),
                                                tqdm_instance=tqdm_obj),
                        'application/octet-stream',
                        None
                    ))
                except ValueError:
                    msg = 'File "{0}" is outside of the base directory "{1}".' \
                          .format(file_path, base_path)
                    raise ValueError(msg) from None

            rqst = Request('POST', '/folders/{}/upload'.format(self.name),
                           config=self.config)
            rqst.content = fields
            resp = yield rqst
        return resp

    def _delete_files(self, files: Sequence[Union[str, Path]]):
        resp = yield Request('GET', '/folders/{}/delete_files'.format(self.name), {
            'files': files,
        }, config=self.config)
        return resp

    def _download(self, files: Sequence[Union[str, Path]],
                  show_progress: bool=False):
        async def _stream_download():
            rqst = Request('GET', '/folders/{}/download'.format(self.name), {
                'files': files,
            }, config=self.config)
            rqst.date = datetime.now(tzutc())
            rqst.headers['Date'] = rqst.date.isoformat()
            try:
                sess = aiohttp.ClientSession()
                rqst._sign()
                async with _timeout(None):
                    rqst_ctx = sess.request(rqst.method,
                                            rqst.build_url(),
                                            data=rqst.pack_content(),
                                            headers=rqst.headers)
                    async with rqst_ctx as resp:
                        total_bytes = resp.content_length
                        tqdm_obj = tqdm(desc='Downloading files',
                                        unit='bytes', unit_scale=True,
                                        total=total_bytes,
                                        disable=not show_progress)
                        reader = aiohttp.MultipartReader.from_response(resp)
                        with tqdm_obj as pbar:
                            acc_bytes = 0
                            while True:
                                part = await reader.next()
                                if part is None:
                                    break
                                fp = open(part.filename, 'wb')
                                while True:
                                    # default chunk size: 8192
                                    chunk = await part.read_chunk()
                                    if not chunk:
                                        break
                                    fp.write(chunk)
                                    acc_bytes += len(chunk)
                                    pbar.update(len(chunk))
                                fp.close()
                            # TODO: more accurate progress bar update
                            pbar.update(total_bytes - acc_bytes)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                # These exceptions must be bubbled up.
                raise
            except aiohttp.ClientError as e:
                msg = 'Request to the API endpoint has failed.\n' \
                      'Check your network connection and/or the server status.'
                raise BackendClientError(msg) from e
            finally:
                if sess:
                    await sess.close()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(_stream_download())
        loop.close()

    def _list_files(self, path: Union[str, Path]='.'):
        resp = yield Request('GET', '/folders/{}/files'.format(self.name), {
            'path': path,
        }, config=self.config)
        return resp.json()

    def __init__(self, name: str, *, config: APIConfig=None):
        assert _rx_slug.search(name) is not None
        self.name = name
        self.config = config
        self.delete   = self._call_base_method(self._delete)
        self.info     = self._call_base_method(self._info)
        self.upload   = self._call_base_method(self._upload)
        self.delete_files = self._call_base_method(self._delete_files)
        # self.download = self._call_base_method(self._download)
        # To deliver loop and session objects to Request.send method.
        # TODO: Generalized request/response abstraction accounting for streaming
        #       would be needed.
        self.download = self._download
        self.list_files = self._call_base_method(self._list_files)

    def __init_subclass__(cls):
        cls.create = cls._call_base_clsmethod(cls._create)
        cls.list   = cls._call_base_clsmethod(cls._list)
        cls.get    = cls._call_base_clsmethod(cls._get)


class VFolder(SyncFunctionMixin, BaseVFolder):
    pass
