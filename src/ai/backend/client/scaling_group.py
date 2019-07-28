from .base import api_function
from .request import Request

__all__ = (
    'ScalingGroup',
)


class ScalingGroup:
    '''
    Provides getting scaling-group information required for the current user.

    The scaling-group is an opaque server-side configuration which splits the whole
    cluster into several partitions, so that server administrators can apply different auto-scaling
    policies and operation standards to each partition of agent sets.
    '''

    session = None
    '''The client session instance that this function class is bound to.'''

    def __init__(self, name: str):
        self.name = name

    @api_function
    @classmethod
    async def list_available(cls, group: str):
        '''
        List available scaling groups for the current user,
        considering the user, the user's domain, and the designated user group.
        '''
        rqst = Request(cls.session, 'GET', '/scaling-groups',
                       params={'group': group})
        async with rqst.fetch() as resp:
            return await resp.json()
