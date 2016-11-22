import uuid

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


def test_auth(defconfig):
    random_msg = uuid.uuid4().hex
    req = Request('GET', '/authorize', {
        'echo': random_msg,
    })
    sign(req)
    resp = req.send()
    assert resp.status == 200
    data = resp.json()
    assert data['authorized'] == 'yes'
    assert data['echo'] == random_msg
