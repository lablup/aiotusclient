'''
Integration Test Suite for Sorna Client API Library.

You should be running the API service on http://localhost:8081 to run this test
suite.  Of course, the service must be fully configured as follows:

 - The gateway server must have at least one agent.
 - The agent should have access to a Docker daemon and the
   "lablup/kernel-python3" docker image.
 - The gateway must have access to a test database that has pre-populated
   fixture data.
   (Check out `python -m sorna.gateway.models --populate-fixtures`)
'''

import uuid

import pytest

from sorna.request import Request
from sorna.kernel import create_kernel, destroy_kernel, \
                         get_kernel_info, execute_code
from sorna.exceptions import SornaAPIError


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
    info = get_kernel_info(kernel_id)
    assert info['lang'] == 'python3'
    assert info['age'] > 0
    assert info['numQueriesExecuted'] == 0
    info = get_kernel_info(kernel_id)
    assert info['numQueriesExecuted'] == 1
    destroy_kernel(kernel_id)
    with pytest.raises(SornaAPIError) as e:
        info = get_kernel_info(kernel_id)
        assert e.status == 404


def test_kernel_execution(defconfig):
    kernel_id = create_kernel('python3')
    result = execute_code(kernel_id, 'code-001', 'print("hello world")')
    assert 'hello world' in result['stdout']
    assert result['stderr'] == ''
    assert len(result['media']) == 0
    assert len(result['exceptions']) == 0
    info = get_kernel_info(kernel_id)
    assert info['numQueriesExecuted'] == 1
    destroy_kernel(kernel_id)
