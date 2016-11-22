import uuid

import pytest

from sorna.request import Request
from sorna.kernel import create_kernel, destroy_kernel, get_kernel_info


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


def test_kernel_lifecycles(defconfig):
    kernel_id = create_kernel('python3')
    print(get_kernel_info(kernel_id))
    destroy_kernel(kernel_id)
