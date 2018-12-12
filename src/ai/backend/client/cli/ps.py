from argparse import Namespace

from . import register_command
from .admin.sessions import sessions


@register_command
def ps(args):
    '''
    Lists the current running compute sessions for the current keypair.
    This is an alias of the "admin sessions --status=RUNNING" command.
    '''
    inner_args = Namespace()
    inner_args.status = 'RUNNING'
    inner_args.access_key = None
    inner_args.id_only = args.id_only
    sessions(inner_args)


ps.add_argument('--id-only', action='store_true', default=False,
                help='Display session ids only.')
