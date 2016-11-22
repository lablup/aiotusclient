from .config import get_config
from .request import Request


def create_kernel(kernel_type, max_mem=0, timeout=0, config=None):
    config = get_config()
    req = Request('POST', '/kernel/create', {
        'lang': kernel_type,
        'resourceLimits': {
            'maxMem': max_mem,
            'timeout': timeout,
        }
    }, config=config)
    resp = req.send()
    assert resp.status == 200
