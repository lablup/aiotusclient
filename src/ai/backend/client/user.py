from typing import Iterable, Sequence, Union

from .base import api_function
from .auth import AuthToken, AuthTokenTypes
from .request import Request

__all__ = (
    'User',
)


class User:
    '''
    Provides interactions with users.
    '''

    session = None
    '''The client session instance that this function class is bound to.'''

    @api_function
    @classmethod
    async def authorize(cls, username: str, password: str, *,
                        token_type: AuthTokenTypes = AuthTokenTypes.KEYPAIR) -> AuthToken:
        """
        Authorize the given credentials and get the API authentication token.
        This function can be invoked anonymously; i.e., it does not require
        access/secret keys in the session config as its purpose is to "get" them.

        Its functionality will be expanded in the future to support multiple types
        of authentication methods.
        """
        rqst = Request(cls.session, 'POST', '/auth/authorize')
        rqst.set_json({
            'type': token_type.value,
            'domain': cls.session.config.domain,
            'username': username,
            'password': password,
        })
        async with rqst.fetch() as resp:
            data = await resp.json()
            return AuthToken(
                type=token_type,
                content=data['data'],
            )
