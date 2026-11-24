import io
import ssl
from dataclasses import dataclass
from typing import AsyncIterator, Iterator, List
from unittest import mock

import aiohttp
import pytest
import pytest_asyncio
from aiohttp import web
from aiohttp.test_utils import TestServer
from aiotusclient.client import TusClient
from aiotusclient.exceptions import TusCertificateError

_CONTENT = b"hello tus"
_CHUNK_SIZE = 4


class _TusServer:
    """Keeps the uploaded bytes and answers the given requests with 500."""

    def __init__(self, failing_patches: List[int], failing_heads: List[int]) -> None:
        self.received = b""
        self._failing_patches = failing_patches
        self._failing_heads = failing_heads
        self._patch_count = 0
        self._head_count = 0

    async def patch(self, request: web.Request) -> web.Response:
        self._patch_count += 1
        if self._patch_count in self._failing_patches:
            return web.Response(status=500)
        assert int(request.headers["Upload-Offset"]) == len(self.received)
        self.received += await request.read()
        return web.Response(
            status=204, headers={"Upload-Offset": str(len(self.received))}
        )

    async def head(self, request: web.Request) -> web.Response:
        self._head_count += 1
        if self._head_count in self._failing_heads:
            return web.Response(status=500)
        return web.Response(headers={"Upload-Offset": str(len(self.received))})


@dataclass(frozen=True)
class _OutageCase:
    id: str
    failing_patches: List[int]
    failing_heads: List[int]


@dataclass(frozen=True)
class _Upload:
    server: _TusServer
    url: str


class TestAsyncUploader:
    @pytest_asyncio.fixture
    async def upload_during_outage(self, case: _OutageCase) -> AsyncIterator[_Upload]:
        tus_server = _TusServer(case.failing_patches, case.failing_heads)
        app = web.Application()
        app.router.add_route("PATCH", "/upload", tus_server.patch)
        app.router.add_route("HEAD", "/upload", tus_server.head)
        async with TestServer(app) as server:
            yield _Upload(server=tus_server, url=str(server.make_url("/upload")))

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "case",
        [
            _OutageCase(id="chunk-fails", failing_patches=[2], failing_heads=[]),
            _OutageCase(
                id="chunk-and-offset-fail", failing_patches=[2], failing_heads=[1]
            ),
        ],
        ids=lambda case: case.id,
    )
    async def test_resumes_after_outage(self, upload_during_outage: _Upload) -> None:
        uploader = TusClient().async_uploader(
            file_stream=io.BytesIO(_CONTENT),
            url=upload_during_outage.url,
            chunk_size=_CHUNK_SIZE,
            retries=3,
            retry_delay=0,
        )

        await uploader.upload()

        assert upload_during_outage.server.received == _CONTENT

    @pytest.fixture
    def patch_with_certificate_error(self) -> Iterator[mock.MagicMock]:
        certificate_error = aiohttp.ClientConnectorCertificateError(
            mock.MagicMock(host="tus.example", port=443),
            ssl.SSLCertVerificationError(1, "certificate verify failed"),
        )
        with mock.patch.object(
            aiohttp.ClientSession, "patch", side_effect=certificate_error
        ) as session_patch:
            yield session_patch

    @pytest.mark.asyncio
    async def test_does_not_retry_certificate_error(
        self, patch_with_certificate_error: mock.MagicMock
    ) -> None:
        uploader = TusClient().async_uploader(
            file_stream=io.BytesIO(_CONTENT),
            url="https://tus.example/upload",
            retries=3,
            retry_delay=0,
        )

        with pytest.raises(TusCertificateError):
            await uploader.upload()

        assert patch_with_certificate_error.call_count == 1
