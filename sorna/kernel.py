import uuid

from .config import get_config
from .exceptions import SornaAPIError
from .request import Request


def create_kernel(kernel_type, client_token=None, max_mem=0, timeout=0):
    if client_token is not None:
        assert isinstance(client_token, str)
        assert len(client_token) > 8
    request = Request('POST', '/kernel/create', {
        'lang': kernel_type,
        'clientSessionToken': client_token if client_token else uuid.uuid4().hex,
        'resourceLimits': {
            'maxMem': max_mem,
            'timeout': timeout,
        }
    })
    request.sign()
    resp = request.send()
    if resp.status == 201:
        return resp.json()['kernelId']
    else:
        raise SornaAPIError(resp.status, resp.reason, resp.text())


def destroy_kernel(kernel_id):
    request = Request('DELETE', '/kernel/{}'.format(kernel_id))
    request.sign()
    resp = request.send()
    if resp.status != 204:
        raise SornaAPIError(resp.status, resp.reason, resp.text())


def get_kernel_info(kernel_id):
    request = Request('GET', '/kernel/{}'.format(kernel_id))
    request.sign()
    resp = request.send()
    if resp.status == 200:
        print(resp.json())
        return resp.json()
    else:
        raise SornaAPIError(resp.status, resp.reason, resp.text())
