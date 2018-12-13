from . import main
from .. import __version__
from ..config import get_config


@main.command()
def config():
    '''
    Shows the current configuration.
    '''
    config = get_config()
    print('Client version: {0}'.format(__version__))
    print('API endpoint: {0}'.format(config.endpoint))
    print('API version: {0}'.format(config.version))
    print('Access key: "{0}"'.format(config.access_key))
    masked_skey = config.secret_key[:6] + ('*' * 24) + config.secret_key[-10:]
    print('Secret key: "{0}"'.format(masked_skey))
    print('Signature hash type: {0}'.format(config.hash_type))
