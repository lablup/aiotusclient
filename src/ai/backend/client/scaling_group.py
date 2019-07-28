from .base import api_function
from .request import Request

__all__ = (
    'ScalingGroup',
)


class ScalingGroup:

    session = None
    '''The client session instance that this function class is bound to.'''

    def __init__(self, name: str):
        self.name = name

    @api_function
    @classmethod
    async def list_available(cls, group: str = None):
        rqst = Request(cls.session, 'GET', '/scaling-groups',
                       params={'group': group})
        async with rqst.fetch() as resp:
            return await resp.json()
