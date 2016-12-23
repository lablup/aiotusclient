import uuid

from .exceptions import SornaAPIError
from .request import Request


def create_kernel(kernel_type, client_token=None, max_mem=0, timeout=0, return_id_only=True):
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
        if return_id_only:
            return resp.json()['kernelId']
        return resp.json()
    else:
        raise SornaAPIError(resp.status, resp.reason, resp.text())


def destroy_kernel(kernel_id):
    request = Request('DELETE', '/kernel/{}'.format(kernel_id))
    request.sign()
    resp = request.send()
    if resp.status != 204:
        raise SornaAPIError(resp.status, resp.reason, resp.text())


def restart_kernel(kernel_id):
    request = Request('PATCH', '/kernel/{}'.format(kernel_id))
    request.sign()
    resp = request.send()
    if resp.status != 204:
        raise SornaAPIError(resp.status, resp.reason, resp.text())


def get_kernel_info(kernel_id):
    request = Request('GET', '/kernel/{}'.format(kernel_id))
    request.sign()
    resp = request.send()
    if resp.status == 200:
        return resp.json()
    else:
        raise SornaAPIError(resp.status, resp.reason, resp.text())


def execute_code(kernel_id, code_id, code):
    request = Request('POST', '/kernel/{}'.format(kernel_id), {
        'codeId': code_id,
        'code': code,
    })
    request.sign()
    resp = request.send()
    if resp.status == 200:
        return resp.json()['result']
    else:
        raise SornaAPIError(resp.status, resp.reason, resp.text())
