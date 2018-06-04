from pathlib import Path

from . import register_command
from .pretty import print_wait, print_done, print_fail
from ..exceptions import BackendError
from ..kernel import Kernel


@register_command
def upload(args):
    """
    Upload files to user's home folder.
    """
    try:
        print_wait('Uploading files...')
        kernel = Kernel(args.sess_id_or_alias)
        kernel.upload(args.files, show_progress=True)
        print_done('Uploaded.')
    except BackendError as e:
        print_fail(str(e))


upload.add_argument('sess_id_or_alias', metavar='NAME',
                    help=('The session ID or its alias given when creating the'
                          'session.'))
upload.add_argument('files', type=Path, nargs='+', help='File paths to upload.')


@register_command
def download(args):
    """
    Download files from a running container.
    """
    try:
        print_wait('Downloading file(s) from {}...'.format(args.sess_id_or_alias))
        kernel = Kernel(args.sess_id_or_alias)
        kernel.download(args.files, show_progress=True)
        print_done('Downloaded.')
    except BackendError as e:
        print_fail(str(e))


download.add_argument('sess_id_or_alias', metavar='NAME',
                      help=('The session ID or its alias given when creating the'
                            'session.'))
download.add_argument('files', nargs='+',
                      help='File paths inside container')
