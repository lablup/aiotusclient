import io
import tarfile

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
        result = kernel.download(args.file)

        # Write file contents in the current directory.
        fileobj = io.BytesIO(result.content)
        with tarfile.TarFile(fileobj=fileobj) as tarobj:
            tarobj.extractall()
        print_done('downloaded {}.'.format(target))
    except BackendError as e:
        print_fail(str(e))


download.add_argument('sess_id_or_alias', metavar='NAME',
                      help=('The session ID or its alias given when creating the'
                            'session.'))
download.add_argument('file', metavar='FILE',
                      help='Target file path to be downloaded from container.')
