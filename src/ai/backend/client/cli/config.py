from . import register_command
from ..config import get_config


@register_command
def config(args):
    '''
    Shows the current configuration.
    '''
    config = get_config()
    print('API endpoint: "{0}"'.format(config.endpoint))
    print('API version: "{0}"'.format(config.version))
    print('Access key: "{0}"'.format(config.access_key))
    masked_skey = config.secret_key[:6] + ('*' * 24) + config.secret_key[-10:]
    print('Secret key: "{0}"'.format(masked_skey))
    print('Signature hash type: "{0}"'.format(config.hash_type))
