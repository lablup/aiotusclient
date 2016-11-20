import pytest

from sorna.request import Request
from sorna.auth import sign


def test_connection(defconfig):
    req = Request('GET', '/')
    resp = req.send()
    assert 'version' in resp.json()


@pytest.mark.asyncio
async def test_async_connection(defconfig):
    req = Request('GET', '/')
    resp = await req.asend()
    assert 'version' in resp.json()


def test_auth():
    pass
