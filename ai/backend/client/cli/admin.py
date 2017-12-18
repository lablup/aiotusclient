import traceback

from tabulate import tabulate

from . import register_command
from .pretty import print_fail
from ..admin import Admin
from ..keypair import KeyPair


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
def keypairs(args):
    '''
    Manage the keypairs.
    Without arguments it shows the list of keypairs.
    '''
    fields = [
        ('Access Key', 'access_key'),
        ('Secret Key', 'secret_key'),
        ('Active?', 'is_active'),
        ('Admin?', 'is_admin'),
        ('Created At', 'created_at'),
        ('Last Used', 'last_used'),
        ('Res.Policy', 'resource_policy'),
        ('Rate Limit', 'rate_limit'),
        ('Concur.Limit', 'concurrency_limit'),
    ]
    items = KeyPair.list(args.user_id, args.is_active,
                         fields=(item[1] for item in fields))
    if len(items) == 0:
        print('There is no matching keypairs associated '
              'with the user ID {0}'.format(args.user_id))
        return
    print(tabulate((item.values() for item in items),
                   headers=(item[0] for item in fields)))


keypairs.add_argument('-u', '--user-id', type=int, default=0,
                      help='Show keypairs of this given user. '
                           '[default: 0]')
keypairs.add_argument('--is-active', type=bool, default=None,
                      help='Filter keypairs by activation.')


@keypairs.register_command
def add(args):
    '''
    Add a new keypair.
    '''
    if args.user_id is None:
        print('You must set the user ID (-u/--user-id).')
        return
    data = KeyPair.create(args.user_id)
    if not data['ok']:
        print('KeyPair creation has failed: {0}'.format(data['msg']))
        return
    item = data['keypair']
    print('Access Key: {0}'.format(item['access_key']))
    print('Secret Key: {0}'.format(item['secret_key']))


add.add_argument('-u', '--user-id', type=int, default=None,
                 help='Create a keypair for this user.')


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
