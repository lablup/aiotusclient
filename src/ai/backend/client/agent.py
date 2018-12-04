from typing import Iterable

from .base import api_function
from .request import Request

__all__ = (
    'Agent',
)


class Agent:
    '''
    Provides a shortcut of :func:`Admin.query()
    <ai.backend.client.admin.Admin.query>` that fetches various agent
    information.

    .. note::

      All methods in this function class require your API access key to
      have the *admin* privilege.
    '''

    session = None
    '''The client session instance that this function class is bound to.'''

    @api_function
    @classmethod
    async def list(cls,
                   status: str = 'ALIVE',
                   fields: Iterable[str] = None):
        '''
        Returns the list of agents with the given status.

        :param status: An upper-cased string constant representing agent
            status (one of ``'ALIVE'``, ``'TERMINATED'``, ``'LOST'``,
            etc.)
        :param fields: Additional per-agent query fields to fetch.
        '''
        if fields is None:
            fields = (
                'id',
                'addr',
                'status',
                'first_contact',
                'mem_slots',
                'cpu_slots',
                'gpu_slots',
            )
        q = 'query($status: String) {' \
            '  agents(status: $status) {' \
            '    $fields' \
            '  }' \
            '}'
        q = q.replace('$fields', ' '.join(fields))
        variables = {
            'status': status,
        }
        rqst = Request(cls.session, 'POST', '/admin/graphql')
        rqst.set_json({
            'query': q,
            'variables': variables,
        })
        async with rqst.fetch() as resp:
            data = await resp.json()
            return data['agents']
