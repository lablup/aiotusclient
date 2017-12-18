from typing import Optional, Iterable

from .base import BaseFunction, SyncFunctionMixin
from .admin import Admin

__all__ = (
    'BaseKeyPair',
    'KeyPair',
)


class BaseKeyPair(BaseFunction):

    @classmethod
    def create(cls, user_id: int,
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
            '    ok msg' \
            '    keypair { $fields }' \
            '  }' \
            '}'
        q = q.replace('$fields', ' '.join(fields))
        data = Admin.query(q, {
            'user_id': user_id,
            'input': {
                'is_active': is_active,
                'is_admin': is_admin,
                'resource_policy': resource_policy,
                'rate_limit': rate_limit,
                'concurrency_limit': concurrency_limit,
            },
        })
        if not data['ok']:
            raise RuntimeError(data['msg'])
        return data['keypair']

    @classmethod
    def list(cls, user_id: int,
             is_active: Optional[bool]=None,
             fields: Optional[Iterable[str]]=None):
        if fields is None:
            fields = (
                'access_key', 'secret_key',
                'is_active', 'is_admin',
                'resource_policy', 'rate_limit', 'concurrency_limit',
            )
        q = 'query($user_id: Int!, $is_active: Boolean) {' \
            '  keypairs(user_id: $user_id, is_active: $is_active) {' \
            '    $fields' \
            '  }' \
            '}'
        q = q.replace('$fields', ' '.join(fields))
        data = Admin.query(q, {
            'user_id': user_id,
            'is_active': is_active,
        })
        return data['keypairs']

    @classmethod
    def activate(cls, access_key: str):
        raise NotImplementedError

    @classmethod
    def deactivate(cls, access_key: str):
        raise NotImplementedError


class KeyPair(SyncFunctionMixin, BaseKeyPair):
    pass
