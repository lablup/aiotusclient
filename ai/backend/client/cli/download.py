from . import register_command
from .pretty import print_wait, print_done, print_fail
from ..exceptions import BackendError
from ..kernel import Kernel


@register_command
def download(args):
    """
    List files in a path of a running container.
    """
    try:
        target = args.file.split('/')[-1]
        print_wait('Downloading file(s) from {}...'.format(args.sess_id_or_alias))
        kernel = Kernel(args.sess_id_or_alias)
        kernel.download(args.file, show_progress=True)
        print_done('downloaded {}.'.format(target))
    except BackendError as e:
        print_fail(str(e))


download.add_argument('sess_id_or_alias', metavar='NAME',
                      help=('The session ID or its alias given when creating the'
                            'session.'))
download.add_argument('file', metavar='FILE',
                      help='Target file path to be downloaded from container.')
