from typing import Iterable, Sequence

from .base import api_function
from .request import Request

__all__ = (
    'Image',
)


class Image:
    '''
    Provides a shortcut of :func:`Admin.query()
    <ai.backend.client.admin.Admin.query>` that fetches the information about
    available images.
    '''

    session = None
    '''The client session instance that this function class is bound to.'''

    @api_function
    @classmethod
    async def list(cls,
                   fields: Iterable[str] = None) -> Sequence[dict]:
        '''
        Fetches the list of registered images in this cluster.
        '''

        if fields is None:
            fields = (
                'name',
                'tag',
                'hash',
            )
        q = 'query {' \
            '  images {' \
            '    $fields' \
            '  }' \
            '}'
        q = q.replace('$fields', ' '.join(fields))
        rqst = Request(cls.session, 'POST', '/admin/graphql')
        rqst.set_json({
            'query': q,
        })
        async with rqst.fetch() as resp:
            data = await resp.json()
            return data['images']
