import os
from typing import Optional

_config = None


class APIConfig:

    DEFAULTS = {
        'endpoint': 'https://api.sorna.io',
        'user_agent': 'Sorna Client Library (Python/v0.1)',
        'version': 'v2.20170315',
    }

    def __init__(self, endpoint: Optional[str]=None,
                 version: str='v2.20170315',
                 user_agent: Optional[str]=None,
                 access_key: Optional[str]=None,
                 secret_key: Optional[str]=None,
                 hash_type: Optional[str]=None) -> None:
        self._endpoint = \
            endpoint if endpoint else os.environ.get('SORNA_ENDPOINT',
                                                     self.DEFAULTS['endpoint'])
        self._version = \
            version if version else self.DEFAULTS['version']
        self._user_agent = \
            user_agent if user_agent else self.DEFAULTS['user_agent']
        self._access_key = \
            access_key if access_key else os.environ['SORNA_ACCESS_KEY']
        self._secret_key = \
            secret_key if secret_key else os.environ['SORNA_SECRET_KEY']
        self._hash_type = \
            hash_type.lower() if hash_type else 'sha256'

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def user_agent(self):
        return self._user_agent

    @property
    def access_key(self):
        return self._access_key

    @property
    def secret_key(self):
        return self._secret_key

    @property
    def version(self):
        return self._version

    @property
    def hash_type(self):
        return self._hash_type


def get_config():
    global _config
    if _config is None:
        _config = APIConfig()
    return _config


def set_config(conf: APIConfig):
    global _config
    _config = conf
