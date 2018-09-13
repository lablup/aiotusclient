import sys

from tabulate import tabulate

from ...exceptions import BackendError
from ...session import Session
from ..pretty import print_fail
from . import admin


@admin.register_command
def vfolders(args):
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
    if args.access_key is None:
        q = 'query { vfolders { $fields } }'
    else:
        q = 'query($ak:String) { vfolders(access_key:$ak) { $fields } }'
    q = q.replace('$fields', ' '.join(item[1] for item in fields))
    with Session() as session:
        try:
            resp = session.Admin.query(q)
        except BackendError as e:
            print_fail(str(e))
            sys.exit(1)
        print(tabulate((item.values() for item in resp['vfolders']),
                       headers=(item[0] for item in fields)))


vfolders.add_argument('--access-key', type=str, default=None,
                      help='Get vfolders for the given access key '
                           '(only works if you are a super-admin)')
