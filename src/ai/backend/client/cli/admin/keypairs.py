import sys

import click
from tabulate import tabulate

from . import admin
from ...session import Session
from ..pretty import print_error, print_fail


@admin.command()
def keypair():
    '''
    Show the server-side information of the currently configured access key.
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
    with Session() as session:
        try:
            kp = session.KeyPair(session.config.access_key)
            info = kp.info(fields=(item[1] for item in fields))
        except Exception as e:
            print_error(e)
            sys.exit(1)
        rows = []
        for name, key in fields:
            rows.append((name, info[key]))
        print(tabulate(rows, headers=('Field', 'Value')))


@admin.group(invoke_without_command=True)
@click.pass_context
@click.option('-u', '--user-id', type=str, default=None,
              help='Show keypairs of this given user. [default: show all]')
@click.option('--is-active', type=bool, default=None,
              help='Filter keypairs by activation.')
def keypairs(ctx, user_id, is_active):
    '''
    List and manage keypairs.
    To show all keypairs or other user's, your access key must have the admin
    privilege.
    (admin privilege required)
    '''
    if ctx.invoked_subcommand is not None:
        return
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
        user_id = int(user_id)
    except (TypeError, ValueError):
        pass  # string-based user ID for Backend.AI v1.4+
    with Session() as session:
        try:
            items = session.KeyPair.list(user_id, is_active,
                                         fields=(item[1] for item in fields))
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if len(items) == 0:
            print('There are no matching keypairs associated '
                  'with the user ID {0}'.format(user_id))
            return
        print(tabulate((item.values() for item in items),
                       headers=(item[0] for item in fields)))


@keypairs.command()
@click.argument('user-id', type=str, default=None, metavar='USERID')
@click.option('-a', '--admin', is_flag=True,
              help='Give the admin privilege to the new keypair.')
@click.option('-i', '--inactive', is_flag=True,
              help='Create the new keypair in inactive state.')
@click.option('-c', '--concurrency-limit', type=int, default=1,
              help='Set the limit on concurrent sessions.')
@click.option('-r', '--rate-limit', type=int, default=5000,
              help='Set the API query rate limit.')
@click.option('--resource-policy', type=str, default=None,
              help='Set the resource policy. (reserved for future use)')
def add(user_id, admin, inactive, concurrency_limit, rate_limit, resource_policy):
    '''
    Add a new keypair.

    USER_ID: User ID of a new key pair.
    '''
    try:
        user_id = int(user_id)
    except ValueError:
        pass  # string-based user ID for Backend.AI v1.4+
    with Session() as session:
        try:
            data = session.KeyPair.create(
                user_id,
                is_active=not inactive,
                is_admin=admin,
                resource_policy=resource_policy,
                rate_limit=rate_limit,
                concurrency_limit=concurrency_limit)
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if not data['ok']:
            print_fail('KeyPair creation has failed: {0}'
                       .format(data['msg']))
            sys.exit(1)
        item = data['keypair']
        print('Access Key: {0}'.format(item['access_key']))
        print('Secret Key: {0}'.format(item['secret_key']))
