from tabulate import tabulate

from ...keypair import KeyPair
from ...exceptions import BackendClientError
from ..pretty import print_fail
from . import admin


@admin.register_command
def keypairs(args):
    '''
    List and manage keypairs.
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
    try:
        items = KeyPair.list(args.user_id, args.is_active,
                             fields=(item[1] for item in fields))
    except BackendClientError as e:
        print_fail(str(e))
        return
    if len(items) == 0:
        print('There are no matching keypairs associated '
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
    try:
        data = KeyPair.create(args.user_id)
    except BackendClientError as e:
        print_fail(str(e))
        return
    if not data['ok']:
        print_fail('KeyPair creation has failed: {0}'
                   .format(data['msg']))
        return
    item = data['keypair']
    print('Access Key: {0}'.format(item['access_key']))
    print('Secret Key: {0}'.format(item['secret_key']))


add.add_argument('-u', '--user-id', type=int, default=None,
                 help='Create a keypair for this user.')
