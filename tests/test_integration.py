'''
Integration Test Suite for Backend Client API Library.

You should be running the API service on http://localhost:8081 to run this test
suite.  Of course, the service must be fully configured as follows:

 - The gateway server must have at least one agent.

   An example sequence to run both manager & agent locally:

   docker run -e POSTGRES_DB=sorna \
              -e POSTGRES_PASSWORD=develove \
              -p 5432:5432 -d \
              --name sorna-db \
              postgres
   python -m ai.backend.client.gateway.models \
          --create-tables --populate-fixtures
   docker run -p 6379:6379 -d \
              --name sorna-redis \
              redis
   python -m ai.backend.client.agent.server --volume-root=`pwd`/volume-temp --max-kernels 3
   python -m ai.backend.client.gateway.server --service-port=8081

 - The agent should have access to a Docker daemon and the
   "lablup/kernel-python3" docker image.

 - The gateway must have access to a test database that has pre-populated
   fixture data.
   (Check out `python -m ai.backend.client.gateway.models --populate-fixtures`)
'''

import textwrap
import time
import uuid

import pytest

from ai.backend.client.request import Request
from ai.backend.client.kernel import (
    create_kernel, destroy_kernel, restart_kernel,
    get_kernel_info, execute_code,
)
from ai.backend.client.exceptions import BackendAPIError


def aggregate_console(c):
    return {
        'stdout': ''.join(item[1] for item in c if item[0] == 'stdout'),
        'stderr': ''.join(item[1] for item in c if item[0] == 'stderr'),
        'html': ''.join(item[1] for item in c if item[0] == 'html'),
        'media': list(item[1] for item in c if item[0] == 'media'),
    }


@pytest.mark.integration
def test_connection(defconfig):
    request = Request('GET', '/')
    resp = request.send()
    assert 'version' in resp.json()


@pytest.mark.integration
def test_not_found(defconfig):
    request = Request('GET', '/invalid-url-wow')
    resp = request.send()
    assert resp.status == 404
    request = Request('GET', '/authorize/uh-oh')
    resp = request.send()
    assert resp.status == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_connection(defconfig):
    request = Request('GET', '/')
    resp = await request.asend()
    assert 'version' in resp.json()


@pytest.mark.integration
def test_auth(defconfig):
    random_msg = uuid.uuid4().hex
    request = Request('GET', '/authorize', {
        'echo': random_msg,
    })
    request.sign()
    resp = request.send()
    assert resp.status == 200
    data = resp.json()
    assert data['authorized'] == 'yes'
    assert data['echo'] == random_msg


@pytest.mark.integration
def test_auth_missing_signature(defconfig):
    random_msg = uuid.uuid4().hex
    request = Request('GET', '/authorize', {
        'echo': random_msg,
    })
    resp = request.send()
    assert resp.status == 401


@pytest.mark.integration
def test_auth_malformed(defconfig):
    request = Request('GET', '/authorize')
    request.content = b'<this is not json>'
    request.sign()
    resp = request.send()
    assert resp.status == 400


@pytest.mark.integration
def test_auth_missing_body(defconfig):
    request = Request('GET', '/authorize')
    request.sign()
    resp = request.send()
    assert resp.status == 400


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_auth(defconfig):
    random_msg = uuid.uuid4().hex
    request = Request('GET', '/authorize', {
        'echo': random_msg,
    })
    request.sign()
    resp = await request.asend()
    assert resp.status == 200
    data = resp.json()
    assert data['authorized'] == 'yes'
    assert data['echo'] == random_msg


@pytest.mark.integration
def test_kernel_lifecycles(defconfig):
    kernel_id = create_kernel('python3')
    info = get_kernel_info(kernel_id)
    assert info['lang'] == 'python3'
    assert info['age'] > 0
    assert info['numQueriesExecuted'] == 0
    info = get_kernel_info(kernel_id)
    assert info['numQueriesExecuted'] == 1
    destroy_kernel(kernel_id)
    # kernel destruction is no longer synchronous!
    time.sleep(2.0)
    with pytest.raises(BackendAPIError) as e:
        info = get_kernel_info(kernel_id)
    assert e.value.args[0] == 404


@pytest.yield_fixture
def py3_kernel():
    kernel_id = create_kernel('python3')
    yield kernel_id
    destroy_kernel(kernel_id)


@pytest.mark.integration
def test_kernel_execution(defconfig, py3_kernel):
    kernel_id = py3_kernel
    result = execute_code(kernel_id, 'print("hello world")')
    console = aggregate_console(result['console'])
    assert 'hello world' in console['stdout']
    assert console['stderr'] == ''
    assert len(console['media']) == 0
    info = get_kernel_info(kernel_id)
    assert info['numQueriesExecuted'] == 1


@pytest.mark.integration
def test_kernel_restart(defconfig, py3_kernel):
    kernel_id = py3_kernel
    first_code = textwrap.dedent('''
    a = "first"
    with open("test.txt", "w") as f:
        f.write("helloo?")
    print(a)
    ''').strip()
    second_code_name_error = textwrap.dedent('''
    print(a)
    ''').strip()
    second_code_file_check = textwrap.dedent('''
    with open("test.txt", "r") as f:
        print(f.read())
    ''').strip()
    result = execute_code(kernel_id, first_code)
    console = aggregate_console(result['console'])
    assert 'first' in console['stdout']
    assert console['stderr'] == ''
    assert len(console['media']) == 0
    restart_kernel(kernel_id)
    result = execute_code(kernel_id, second_code_name_error)
    console = aggregate_console(result['console'])
    assert 'NameError' in console['stderr']
    assert len(console['media']) == 0
    result = execute_code(kernel_id, second_code_file_check)
    console = aggregate_console(result['console'])
    assert 'helloo?' in console['stdout']
    assert console['stderr'] == ''
    assert len(console['media']) == 0
    info = get_kernel_info(kernel_id)
    # FIXME: this varies between 2~4
    assert 2 <= info['numQueriesExecuted'] <= 4
