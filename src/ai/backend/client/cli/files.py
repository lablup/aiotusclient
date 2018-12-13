from datetime import datetime
import json
from pathlib import Path
import sys

import click
from tabulate import tabulate

from . import main
from .pretty import print_wait, print_done, print_error, print_fail
from ..session import Session


@main.command()
@click.argument('sess_id_or_alias', metavar='SESSID')
@click.argument('files', type=click.Path(exists=True), nargs=-1)
def upload(sess_id_or_alias, files):
    """
    Upload files to user's home folder.

    \b
    SESSID: Session ID or its alias given when creating the session.
    FILES: Path to upload.
    """
    if len(files) < 1:
        return
    with Session() as session:
        try:
            print_wait('Uploading files...')
            kernel = session.Kernel(sess_id_or_alias)
            kernel.upload(files, show_progress=True)
            print_done('Uploaded.')
        except Exception as e:
            print_error(e)
            sys.exit(1)


@main.command()
@click.argument('sess_id_or_alias', metavar='SESSID')
@click.argument('files', nargs=-1)
@click.option('--dest', type=Path, default='.',
              help='Destination path to store downloaded file(s)')
def download(sess_id_or_alias, files, dest):
    """
    Download files from a running container.

    \b
    SESSID: Session ID or its alias given when creating the session.
    FILES: Paths inside container.
    """
    if len(files) < 1:
        return
    with Session() as session:
        try:
            print_wait('Downloading file(s) from {}...'
                       .format(sess_id_or_alias))
            kernel = session.Kernel(sess_id_or_alias)
            kernel.download(files, dest, show_progress=True)
            print_done('Downloaded to {}.'.format(dest.resolve()))
        except Exception as e:
            print_error(e)
            sys.exit(1)


@main.command()
@click.argument('sess_id_or_alias', metavar='SESSID')
@click.argument('path', metavar='PATH', nargs=1, default='/home/work')
def ls(sess_id_or_alias, path):
    """
    List files in a path of a running container.

    \b
    SESSID: Session ID or its alias given when creating the session.
    PATH: Path inside container.
    """
    with Session() as session:
        try:
            print_wait('Retrieving list of files in "{}"...'.format(path))
            kernel = session.Kernel(sess_id_or_alias)
            result = kernel.list_files(path)

            if 'errors' in result and result['errors']:
                print_fail(result['errors'])
                sys.exit(1)

            files = json.loads(result['files'])
            table = []
            headers = ['file name', 'size', 'modified', 'mode']
            for file in files:
                mdt = datetime.fromtimestamp(file['mtime'])
                mtime = mdt.strftime('%b %d %Y %H:%M:%S')
                row = [file['filename'], file['size'], mtime, file['mode']]
                table.append(row)
            print_done('Retrived.')
            print('Path in container:', result['abspath'], end='')
            print(tabulate(table, headers=headers))
        except Exception as e:
            print_error(e)
            sys.exit(1)
