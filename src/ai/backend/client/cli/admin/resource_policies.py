import sys
from typing import Sequence

import click
from tabulate import tabulate

from . import admin
from ...session import Session
from ..pretty import print_error, print_fail


@admin.command()
@click.argument('name', type=str, default=None, metavar='NAME')
def resource_policy(name):
    """
    Show details about a keypair resource policy.
    (admin privilege required)
    """
    fields = [
        ('Name', 'name'),
        ('Created At', 'created_at'),
        ('Default for Unspecified', 'default_for_unspecified'),
        ('Total Resource Slot', 'total_resource_slots'),
        ('Max Concurrent Sessions', 'max_concurrent_sessions'),
        ('Max Containers per Session', 'max_containers_per_session'),
        ('Max vFolder Count', 'max_vfolder_count'),
        ('Max vFolder Size', 'max_vfolder_size'),
        ('Idle Timeeout', 'idle_timeout'),
        ('Allowed vFolder Hosts', 'allowed_vfolder_hosts'),
    ]
    with Session() as session:
        try:
            rp = session.ResourcePolicy(session.config.access_key)
            info = rp.info(name, fields=(item[1] for item in fields))
        except Exception as e:
            print_error(e)
            sys.exit(1)
        rows = []
        if info is None:
            print('No such resource policy.')
            sys.exit(1)
        for name, key in fields:
            rows.append((name, info[key]))
        print(tabulate(rows, headers=('Field', 'Value')))


@admin.group(invoke_without_command=True)
@click.pass_context
def resource_policies(ctx):
    '''
    List and manage resource policies.
    (admin privilege required)
    '''
    if ctx.invoked_subcommand is not None:
        return
    fields = [
        ('Name', 'name'),
        ('Created At', 'created_at'),
        ('Default for Unspecified', 'default_for_unspecified'),
        ('Total Resource Slot', 'total_resource_slots'),
        ('Max Concurrent Sessions', 'max_concurrent_sessions'),
        ('Max Containers per Session', 'max_containers_per_session'),
        ('Max vFolder Count', 'max_vfolder_count'),
        ('Max vFolder Size', 'max_vfolder_size'),
        ('Idle Timeeout', 'idle_timeout'),
        ('Allowed vFolder Hosts', 'allowed_vfolder_hosts'),
    ]
    with Session() as session:
        try:
            items = session.ResourcePolicy.list(fields=(item[1] for item in fields))
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if len(items) == 0:
            print('There are no keypair resource policies.')
            return
        print(tabulate((item.values() for item in items),
                       headers=(item[0] for item in fields)))


@resource_policies.command()
@click.argument('name', type=str, default=None, metavar='NAME')
@click.option('--default-for-unspecified', type=str, default='UNLIMITED',
              help='Default behavior for unspecified resources: '
                   'LIMITED, UNLIMITED')
@click.option('--total-resource-slots', type=str, default='{}',
              help='Set total resource slots.')
@click.option('--max-concurrent-sessions', type=int, default=30,
              help='Number of maximum concurrent sessions.')
@click.option('--max-containers-per-session', type=int, default=1,
              help='Number of maximum containers per session.')
@click.option('--max-vfolder-count', type=int, default=10,
              help='Number of maximum virtual folders allowed.')
@click.option('--max-vfolder-size', type=int, default=0,
              help='Maximum virtual folder size (future plan).')
@click.option('--idle-timeout', type=int, default=1800,
              help='The maximum period of time allowed for kernels to wait '
                   'further requests.')
# @click.option('--allowed-vfolder-hosts', type=click.Tuple(str), default=['local'],
#               help='Locations to create virtual folders.')
@click.option('--allowed-vfolder-hosts', default=['local'],
              help='Locations to create virtual folders.')
def add(name, default_for_unspecified, total_resource_slots, max_concurrent_sessions,
        max_containers_per_session, max_vfolder_count, max_vfolder_size,
        idle_timeout, allowed_vfolder_hosts):
    '''
    Add a new keypair resource policy.

    NAME: NAME of a new keypair resource policy.
    '''
    with Session() as session:
        try:
            data = session.ResourcePolicy.create(
                name,
                default_for_unspecified=default_for_unspecified,
                total_resource_slots=total_resource_slots,
                max_concurrent_sessions=max_concurrent_sessions,
                max_containers_per_session=max_containers_per_session,
                max_vfolder_count=max_vfolder_count,
                max_vfolder_size=max_vfolder_size,
                idle_timeout=idle_timeout,
                allowed_vfolder_hosts=allowed_vfolder_hosts,
            )
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if not data['ok']:
            print_fail('KeyPair Resource Policy creation has failed: {0}'
                       .format(data['msg']))
            sys.exit(1)
        item = data['resource_policy']
        print('Keypair resource policy ' + item['name'] + ' is created.')
