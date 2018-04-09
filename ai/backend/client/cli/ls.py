from . import register_command
from .pretty import print_wait, print_done, print_fail
from ..exceptions import BackendError
from ..kernel import Kernel


@register_command
def ls(args):
    """
    List files in a path of a running container.
    """
    try:
        path = args.path if args.path else '.'
        print_wait('Retrieving list of files in "{}"...'.format(path))
        kernel = Kernel(args.sess_id_or_alias)
        result = kernel.list_files(path)
        print_done('Retrived.')
        print(result['ls'])
    except BackendError as e:
        print_fail(str(e))


ls.add_argument('sess_id_or_alias', metavar='NAME',
                help='The session ID or its alias given when creating the session.')
ls.add_argument('path', metavar='PATH',
                help='Target path to get list of files.')
