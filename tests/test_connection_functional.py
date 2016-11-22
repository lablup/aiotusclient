import uuid

import pytest

from sorna.request import Request


def test_connection(defconfig):
    rqst = Request('GET', '/')
    resp = rqst.send()
    assert 'version' in resp.json()


@pytest.mark.asyncio
async def test_async_connection(defconfig):
    rqst = Request('GET', '/')
    resp = await rqst.asend()
    assert 'version' in resp.json()


def test_auth(defconfig):
    random_msg = uuid.uuid4().hex
    rqst = Request('GET', '/authorize', {
        'echo': random_msg,
    })
    rqst.sign()
    resp = rqst.send()
    assert resp.status == 200
    data = resp.json()
    assert data['authorized'] == 'yes'
    assert data['echo'] == random_msg


@pytest.mark.asyncio
async def test_async_auth(defconfig):
    random_msg = uuid.uuid4().hex
    rqst = Request('GET', '/authorize', {
        'echo': random_msg,
    })
    rqst.sign()
    resp = await rqst.asend()
    assert resp.status == 200
    data = resp.json()
    assert data['authorized'] == 'yes'
    assert data['echo'] == random_msg
