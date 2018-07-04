import sys

from tabulate import tabulate

from ...exceptions import BackendError
from ...session import Session
from ..pretty import print_fail
from . import admin


@admin.register_command
def keypairs(args):
    '''
    List and manage keypairs.
    '''
    fields = [
        ('User ID', 'user_id'),
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
        args.user_id = int(args.user_id)
    except ValueError:
        pass  # string-based user ID for Backend.AI v1.4+
    with Session() as session:
        try:
            items = session.KeyPair.list(args.user_id, args.is_active,
                                         fields=(item[1] for item in fields))
        except BackendError as e:
            print_fail(str(e))
            sys.exit(1)
        if len(items) == 0:
            print('There are no matching keypairs associated '
                  'with the user ID {0}'.format(args.user_id))
            return
        print(tabulate((item.values() for item in items),
                       headers=(item[0] for item in fields)))


keypairs.add_argument('-u', '--user-id', type=str, default='0',
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
        args.user_id = int(args.user_id)
    except ValueError:
        pass  # string-based user ID for Backend.AI v1.4+
    with Session() as session:
        try:
            data = session.KeyPair.create(
                args.user_id,
                is_active=not args.inactive,
                is_admin=args.admin,
                resource_policy=args.resource_policy,
                rate_limit=args.rate_limit,
                concurrency_limit=args.concurrency_limit)
        except BackendError as e:
            print_fail(str(e))
            sys.exit(1)
        if not data['ok']:
            print_fail('KeyPair creation has failed: {0}'
                       .format(data['msg']))
            sys.exit(1)
        item = data['keypair']
        print('Access Key: {0}'.format(item['access_key']))
        print('Secret Key: {0}'.format(item['secret_key']))


add.add_argument('-u', '--user-id', type=str, default=None,
                 help='Create a keypair for this user.')
add.add_argument('-a', '--admin', action='store_true', default=False,
                 help='Give the admin privilege to the new keypair.')
add.add_argument('-i', '--inactive', action='store_true', default=False,
                 help='Create the new keypair in inactive state.')
add.add_argument('-c', '--concurrency-limit', type=int, default=1,
                 help='Set the limit on concurrent sessions.')
add.add_argument('-r', '--rate-limit', type=int, default=5000,
                 help='Set the API query rate limit.')
add.add_argument('--resource-policy', type=str, default=None,
                 help='Set the resource policy. (reserved for future use)')
