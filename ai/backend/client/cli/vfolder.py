from datetime import datetime
import json
from pathlib import Path
import sys

from tabulate import tabulate

from . import register_command
from .pretty import print_wait, print_done, print_fail
from ..exceptions import BackendError
from ..vfolder import VFolder


@register_command
def vfolder(args):
    '''Provides virtual folder operations.'''
    print('Run with -h/--help for usage.')


@vfolder.register_command
def list(args):
    '''List virtual folders that belongs to the current user.'''
    fields = [
        ('Name', 'name'),
        ('ID', 'id'),
    ]
    try:
        resp = VFolder.list()
        if not resp:
            print('There is no virtual folders created yet.')
            return
        rows = (tuple(vf[key] for _, key in fields) for vf in resp)
        hdrs = (display_name for display_name, _ in fields)
        print(tabulate(rows, hdrs))
    except BackendError as e:
        print_fail(str(e))
        sys.exit(1)


@vfolder.register_command
def create(args):
    '''Create a new virtual folder.'''
    try:
        result = VFolder.create(args.name)
        print('Virtual folder "{0}" is created.'.format(result['name']))
    except BackendError as e:
        print_fail(str(e))
        sys.exit(1)


create.add_argument('name', type=str, help='The name of a virtual folder.')


@vfolder.register_command
def delete(args):
    '''Delete the given virtual folder. This operation is irreversible!'''
    try:
        VFolder(args.name).delete()
    except BackendError as e:
        print_fail(str(e))
        sys.exit(1)


delete.add_argument('name', type=str, help='The name of a virtual folder.')


@vfolder.register_command
def info(args):
    '''Show the information of the given virtual folder.'''
    try:
        result = VFolder(args.name).info()
        print('Virtual folder "{0}" (ID: {1})'.format(result['name'], result['id']))
        print('- Number of files: {0}'.format(result['numFiles']))
    except BackendError as e:
        print_fail(str(e))
        sys.exit(1)


info.add_argument('name', type=str, help='The name of a virtual folder.')


@vfolder.register_command
def upload(args):
    '''Upload a file to the virtual folder from the current working directory.'''
    try:
        VFolder(args.name).upload(args.filenames, show_progress=True)
        print_done('Done.')
    except BackendError as e:
        print_fail(str(e))
        sys.exit(1)


upload.add_argument('name', type=str, help='The name of a virtual folder.')
upload.add_argument('filenames', type=Path, nargs='+',
                    help='Paths of the files to be uploaded.')


@vfolder.register_command
def delete_files(args):
    '''Delete files in a virtual folder. This operation is irreversible!'''
    try:
        if input("> Are you sure? (y/n): ").lower().strip()[:1] == 'y':
            VFolder(args.name).delete_files(args.filenames)
            print_done('Done.')
    except BackendError as e:
        print_fail(str(e))
        sys.exit(1)


delete_files.add_argument('name', type=str, help='The name of a virtual folder.')
delete_files.add_argument('filenames', nargs='+',
                          help='Paths of the files to delete.')


@vfolder.register_command
def download(args):
    '''Download a file from the virtual folder to the current working directory.'''
    try:
        VFolder(args.name).download(args.filenames, show_progress=True)
        print_done('Done.')
    except BackendError as e:
        print_fail(str(e))
        sys.exit(1)


download.add_argument('name', type=str, help='The name of a virtual folder.')
download.add_argument('filenames', nargs='+',
                      help='Paths of the files to download.')


@vfolder.register_command
def ls(args):
    """
    List files in a path of a virtual folder.
    """
    try:
        print_wait('Retrieving list of files in "{}"...'.format(args.path))
        result = VFolder(args.name).list_files(args.path)
        if 'error_msg' in result and result['error_msg']:
            print_fail(result['error_msg'])
            return
        files = json.loads(result['files'])
        table = []
        headers = ['file name', 'size', 'modified', 'mode']
        for file in files:
            mdt = datetime.fromtimestamp(file['mtime'])
            mtime = mdt.strftime('%b %d %Y %H:%M:%S')
            row = [file['filename'], file['size'], mtime, file['mode']]
            table.append(row)
        print_done('Retrived.')
        print('Path in vfolder:', result['folder_path'])
        print(tabulate(table, headers=headers))
    except BackendError as e:
        print_fail(str(e))


ls.add_argument('name', type=str, help='The name of a virtual folder.')
ls.add_argument('path', metavar='PATH', nargs='?', default='.',
                help='Path inside vfolder')


@vfolder.register_command
def invite(args):
    """Invite other users to access the virtual folder.
    """
    try:
        assert args.perm in ['rw', 'ro']
        result = VFolder(args.name).invite(args.perm, args.emails)
        print('Invitation sent.')
    except BackendError as e:
        print_fail(str(e))
        sys.exit(1)


invite.add_argument('name', type=str, help='The name of a virtual folder.')
invite.add_argument('emails', type=str, nargs='+', help='Emails to invite.')
invite.add_argument('-p', '--perm', metavar='PERMISSION', type=str, default='rw',
                    help='Permission to give. "ro" (read-only) / "rw" (read-write).')
