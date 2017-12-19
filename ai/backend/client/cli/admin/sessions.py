from tabulate import tabulate

from ...admin import Admin
from ...exceptions import BackendClientError
from ..pretty import print_fail
from . import admin


@admin.register_command
def sessions(args):
    '''
    List and manage compute sessions.
    '''
    fields = [
        ('Session ID', 'sess_id'),
        ('Lang/runtime', 'lang'),
        ('Created At', 'created_at',),
        ('Termianted At', 'terminated_at'),
        ('Status', 'status'),
        ('Memory Slot', 'mem_slot'),
        ('CPU Slot', 'cpu_slot'),
        ('GPU Slot', 'gpu_slot'),
    ]
    if args.access_key is None:
        q = 'query($status:String) { compute_sessions(status:$status) { $fields } }'
    else:
        q = 'query($ak:String, $status:String) {' \
            '  compute_sessions(access_key:$ak, status:$status) { $fields }' \
            '}'
    q = q.replace('$fields', ' '.join(item[1] for item in fields))
    v = {
        'status': args.status if args.status != 'ALL' else None,
        'ak': args.access_key,
    }
    try:
        resp = Admin.query(q, v)
    except BackendClientError as e:
        print_fail(str(e))
        return
    if len(resp['compute_sessions']) == 0:
        print('There are no compute sessions currently running.')
        return
    print(tabulate((item.values() for item in resp['compute_sessions']),
                   headers=(item[0] for item in fields)))


sessions.add_argument('--status', type=str, default='RUNNING',
                      choices={'PREPARING', 'BUILDING', 'RUNNING',
                               'RESTARTING', 'RESIZING', 'SUSPENDED',
                               'TERMINATING', 'TERMINATED', 'ERROR', 'ALL'},
                      help='Filter by the given status (default: RUNNING)')
sessions.add_argument('--access-key', type=str, default=None,
                      help='Get sessions for a specific access key '
                           '(only works if you are a super-admin)')
