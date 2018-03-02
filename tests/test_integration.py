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
   python -m ai.backend.client.agent.server \
          --volume-root=`pwd`/volume-temp --max-kernels 3
   python -m ai.backend.client.gateway.server --service-port=8081

 - The agent should have access to a Docker daemon and the
   "lablup/kernel-python:latest" docker image.

 - The gateway must have access to a test database that has pre-populated
   fixture data.
   (Check out `python -m ai.backend.client.gateway.models --populate-fixtures`)
'''

import textwrap
import time
import uuid

import pytest

from ai.backend.client.compat import token_hex
from ai.backend.client.request import Request
from ai.backend.client.admin import Admin
from ai.backend.client.kernel import Kernel
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
    # let it bypass actual signing
    request._sign = lambda *args, **kwargs: None
    resp = request.send()
    assert resp.status == 401


@pytest.mark.integration
def test_auth_malformed(defconfig):
    request = Request('GET', '/authorize')
    request.content = b'<this is not json>'
    resp = request.send()
    assert resp.status == 400


@pytest.mark.integration
def test_auth_missing_body(defconfig):
    request = Request('GET', '/authorize')
    resp = request.send()
    assert resp.status == 400


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_auth(defconfig):
    random_msg = uuid.uuid4().hex
    request = Request('GET', '/authorize', {
        'echo': random_msg,
    })
    resp = await request.asend()
    assert resp.status == 200
    data = resp.json()
    assert data['authorized'] == 'yes'
    assert data['echo'] == random_msg


@pytest.mark.integration
def test_kernel_lifecycles(defconfig):
    kernel = Kernel.get_or_create('python:latest')
    kernel_id = kernel.kernel_id
    info = kernel.get_info()
    assert info['lang'] == 'python:latest'
    assert info['numQueriesExecuted'] == 1
    info = kernel.get_info()
    assert info['numQueriesExecuted'] == 2
    kernel.destroy()
    # kernel destruction is no longer synchronous!
    time.sleep(2.0)
    with pytest.raises(BackendAPIError) as e:
        info = Kernel(kernel_id).get_info()
    assert e.value.args[0] == 404


@pytest.yield_fixture
def py3_kernel():
    kernel = Kernel.get_or_create('python:latest')
    yield kernel
    kernel.destroy()


def exec_loop(kernel, code):
    # The server may return continuation if kernel preparation
    # takes a little longer time (a few seconds).
    console = []
    num_queries = 0
    run_id = token_hex(8)
    while True:
        result = kernel.execute(run_id, code if num_queries == 0 else '')
        num_queries += 1
        console.extend(result['console'])
        if result['status'] == 'finished':
            break
    return aggregate_console(console), num_queries


@pytest.mark.integration
def test_kernel_execution(defconfig, py3_kernel):
    console, n = exec_loop(py3_kernel, 'print("hello world"); raise RuntimeError()')
    assert 'hello world' in console['stdout']
    assert 'RuntimeError' in console['stderr']
    assert len(console['media']) == 0
    info = py3_kernel.get_info()
    assert info['numQueriesExecuted'] == n + 1


@pytest.mark.integration
def test_kernel_restart(defconfig, py3_kernel):
    num_queries = 1  # first query is done by py3_kernel fixture (creation)
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
    console, n = exec_loop(py3_kernel, first_code)
    num_queries += n
    assert 'first' in console['stdout']
    assert console['stderr'] == ''
    assert len(console['media']) == 0
    py3_kernel.restart()
    num_queries += 1
    console, n = exec_loop(py3_kernel, second_code_name_error)
    num_queries += n
    assert 'NameError' in console['stderr']
    assert len(console['media']) == 0
    console, n = exec_loop(py3_kernel, second_code_file_check)
    num_queries += n
    assert 'helloo?' in console['stdout']
    assert console['stderr'] == ''
    assert len(console['media']) == 0
    info = py3_kernel.get_info()
    # FIXME: this varies between 2~4
    assert info['numQueriesExecuted'] == num_queries


@pytest.mark.integration
def test_admin_api(defconfig, py3_kernel):
    q = '''
    query($ak: String!) {
        compute_sessions(access_key: $ak, status: "RUNNING") {
            lang
        }
    }'''
    resp = Admin.query(q, {
        'ak': defconfig.access_key,
    })
    assert 'compute_sessions' in resp
    assert len(resp['compute_sessions']) >= 1
    assert resp['compute_sessions'][0]['lang'] == 'python:latest'
