from .base import api_function
from .request import Request

__all__ = (
    'Resource'
)


class Resource:
    """
    Provides interactions with resource.
    """
    session = None
    """The client session instance that this function class is bound to."""

    # def __init__(self, access_key: str):
    #     self.access_key = access_key

    @api_function
    @classmethod
    async def list(cls):
        '''
        Lists all resource presets.
        '''
        rqst = Request(cls.session, 'GET', '/resource/presets')
        async with rqst.fetch() as resp:
            return await resp.json()

    @api_function
    @classmethod
    async def check_presets(cls):
        '''
        Lists all resource presets in the current scaling group with additiona
        information.
        '''
        rqst = Request(cls.session, 'POST', '/resource/check-presets')
        async with rqst.fetch() as resp:
            return await resp.json()
