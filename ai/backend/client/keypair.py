from typing import Optional, Iterable

from .base import BaseFunction, SyncFunctionMixin
from .request import Request

__all__ = (
    'BaseKeyPair',
    'KeyPair',
)


class BaseKeyPair(BaseFunction):

    @classmethod
    def _create(cls, user_id: int,
                is_active: bool=True,
                is_admin: bool=False,
                resource_policy: Optional[str]=None,
                rate_limit: Optional[int]=None,
                concurrency_limit: Optional[int]=None,
                fields: Optional[Iterable[str]]=None):
        if fields is None:
            fields = ('access_key', 'secret_key')
        q = 'mutation($user_id: Int!, $input: KeyPairInput!) {' \
            '  create_keypair(user_id: $user_id, props: $input) {' \
            '    ok msg keypair { $fields }' \
            '  }' \
            '}'
        q = q.replace('$fields', ' '.join(fields))
        vars = {
            'user_id': user_id,
            'input': {
                'is_active': is_active,
                'is_admin': is_admin,
                'resource_policy': resource_policy,
                'rate_limit': rate_limit,
                'concurrency_limit': concurrency_limit,
            },
        }
        resp = yield Request('POST', '/admin/graphql', {
            'query': q,
            'variables': vars,
        })
        data = resp.json()
        return data['create_keypair']

    @classmethod
    def _list(cls, user_id: int,
              is_active: Optional[bool]=None,
              fields: Optional[Iterable[str]]=None):
        if fields is None:
            fields = (
                'access_key', 'secret_key',
                'is_active', 'is_admin',
            )
        q = 'query($user_id: Int!, $is_active: Boolean) {' \
            '  keypairs(user_id: $user_id, is_active: $is_active) {' \
            '    $fields' \
            '  }' \
            '}'
        q = q.replace('$fields', ' '.join(fields))
        vars = {
            'user_id': user_id,
            'is_active': is_active,
        }
        resp = yield Request('POST', '/admin/graphql', {
            'query': q,
            'variables': vars,
        })
        data = resp.json()
        return data['keypairs']

    @classmethod
    def activate(cls, access_key: str):
        raise NotImplementedError

    @classmethod
    def deactivate(cls, access_key: str):
        raise NotImplementedError

    def __init_subclass__(cls):
        cls.create = cls._call_base_clsmethod(cls._create)
        cls.list = cls._call_base_clsmethod(cls._list)


class KeyPair(SyncFunctionMixin, BaseKeyPair):
    pass
