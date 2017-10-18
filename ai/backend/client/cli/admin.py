import traceback

from tabulate import tabulate

from . import register_command
from .pretty import print_fail
from ..admin import Admin


@register_command
def admin(args):
    '''
    Provides the admin API access.
    '''
    print('Run with -h/--help for usage.')


@admin.register_command
def sessions(args):
    '''
    List your compute sessions.
    '''
    fields = [
        ('Session ID', 'id'),
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
    except:
        print_fail('Failed to query the gateway!')
        traceback.print_exc()
        return
    if len(resp['compute_sessions']) == 0:
        print('There is no compute sessions currently running.')
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


@admin.register_command
def vfolders(args):
    '''
    List your virtual folders.
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
    try:
        resp = Admin.query(q)
    except:
        print_fail('Failed to query the gateway!')
        traceback.print_exc()
        return
    print(tabulate((item.values() for item in resp['vfolders']),
                   headers=(item[0] for item in fields)))


vfolders.add_argument('--access-key', type=str, default=None,
                      help='Get vfolders for a specific access key '
                           '(only works if you are a super-admin)')
