import sys

import click
from tabulate import tabulate

from . import admin
from ...session import Session
from ..pretty import print_error


@admin.command()
@click.option('--access-key', type=str, default=None,
              help='Get vfolders for the given access key '
                   '(only works if you are a super-admin)')
def vfolders(access_key):
    '''
    List and manage virtual folders.
    '''
    fields = [
        ('Name', 'name'),
        ('Created At', 'created_at'),
        ('Last Used', 'last_used'),
        ('Max Files', 'max_files'),
        ('Max Size', 'max_size'),
    ]
    if access_key is None:
        q = 'query { vfolders { $fields } }'
    else:
        q = 'query($ak:String) { vfolders(access_key:$ak) { $fields } }'
    q = q.replace('$fields', ' '.join(item[1] for item in fields))
    v = {'ak': access_key}
    with Session() as session:
        try:
            resp = session.Admin.query(q, v)
        except Exception as e:
            print_error(e)
            sys.exit(1)
        print(tabulate((item.values() for item in resp['vfolders']),
                       headers=(item[0] for item in fields)))
