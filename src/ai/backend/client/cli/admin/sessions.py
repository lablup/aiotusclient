import sys

import click
from tabulate import tabulate
import textwrap

from . import admin
from ...helper import is_admin
from ...session import Session, is_legacy_server
from ..pretty import print_error


@admin.command()
@click.option('--status', default='RUNNING',
              type=click.Choice(['PREPARING', 'BUILDING', 'RUNNING', 'RESTARTING',
                                 'RESIZING', 'SUSPENDED', 'TERMINATING',
                                 'TERMINATED', 'ERROR', 'ALL']),
              help='Filter by the given status')
@click.option('--access-key', type=str, default=None,
              help='Get sessions for a specific access key '
                   '(only works if you are a super-admin)')
@click.option('--id-only', is_flag=True, help='Display session ids only.')
@click.option('--all', is_flag=True, help='Display all sessions.')
def sessions(status, access_key, id_only, all):
    '''
    List and manage compute sessions.
    '''
    fields = [
        ('Session ID', 'sess_id'),
    ]
    with Session() as session:
        if is_admin(session):
            fields.append(('Owner', 'access_key'))
    if not id_only:
        fields.extend([
            ('Image', 'image'),
            ('Tag', 'tag'),
            ('Created At', 'created_at',),
            ('Terminated At', 'terminated_at'),
            ('Status', 'status'),
            ('Occupied Resource', 'occupied_slots'),
            ('Used Memory (MiB)', 'mem_cur_bytes'),
            ('Max Used Memory (MiB)', 'mem_max_bytes'),
            ('CPU Using (%)', 'cpu_using'),
        ])
        if is_legacy_server():
            del fields[2]

    def execute_paginated_query(limit, offset):
        q = '''
        query($limit:Int!, $offset:Int!, $ak:String, $status:String) {
          compute_session_list(
              limit:$limit, offset:$offset, access_key:$ak, status:$status) {
            items { $fields }
            total_count
          }
        }'''
        q = textwrap.dedent(q).strip()
        q = q.replace('$fields', ' '.join(item[1] for item in fields))
        v = {
            'limit': limit,
            'offset': offset,
            'status': status if status != 'ALL' else None,
            'ak': access_key,
        }
        try:
            resp = session.Admin.query(q, v)
        except Exception as e:
            print_error(e)
            sys.exit(1)
        return resp['compute_session_list']

    def round_mem(items):
        for item in items:
            if 'mem_cur_bytes' in item:
                item['mem_cur_bytes'] = round(item['mem_cur_bytes'] / 2 ** 20, 1)
            if 'mem_max_bytes' in item:
                item['mem_max_bytes'] = round(item['mem_max_bytes'] / 2 ** 20, 1)
        return items

    def _generate_paginated_results(interval):
        offset = 0
        is_first = True
        total_count = -1
        while True:
            limit = (interval if is_first else
                    min(interval, total_count - offset))
            try:
                result = execute_paginated_query(limit, offset)
            except Exception as e:
                print_error(e)
                sys.exit(1)
            offset += interval
            total_count = result['total_count']
            items = result['items']
            items = round_mem(items)

            if id_only:
                yield '\n'.join([item['sess_id'] for item in items]) + '\n'
            else:
                table = tabulate([item.values() for item in items],
                                    headers=(item[0] for item in fields))
                if not is_first:
                    table_rows = table.split('\n')
                    table = '\n'.join(table_rows[2:])
                yield table + '\n'

            if is_first:
                    is_first = False
            if not offset < total_count:
                break

    with Session() as session:
        paginating_interval = 10
        if all:
            click.echo_via_pager(_generate_paginated_results(paginating_interval))
        else:
            result = execute_paginated_query(paginating_interval, offset=0)
            total_count = result['total_count']
            if total_count == 0:
                print('There are no compute sessions currently {0}.'
                      .format(status.lower()))
                return
            items = result['items']
            items = round_mem(items)
            if id_only:
                for item in items:
                    print(item['sess_id'])
            else:
                print(tabulate([item.values() for item in items],
                                headers=(item[0] for item in fields)))
            if total_count > paginating_interval:
                print("More sessions can be displayed by using --all option.")


@admin.command()
@click.argument('sess_id_or_alias', metavar='SESSID')
@click.option('-o', '--owner', '--owner-access-key', metavar='ACCESS_KEY',
              help='Specify the owner of the target session explicitly.')
def session(sess_id_or_alias):
    '''
    Show detailed information for a running compute session.

    SESSID: Session id or its alias.
    '''
    fields = [
        ('Session ID', 'sess_id'),
        ('Role', 'role'),
        ('Image', 'image'),
        ('Tag', 'tag'),
        ('Created At', 'created_at'),
        ('Terminated At', 'terminated_at'),
        ('Agent', 'agent'),
        ('Status', 'status'),
        ('Status Info', 'status_info'),
        ('Occupied Resources', 'occupied_slots'),
        ('CPU Used (ms)', 'cpu_used'),
        ('Used Memory (MiB)', 'mem_cur_bytes'),
        ('Max Used Memory (MiB)', 'mem_max_bytes'),
        ('Number of Queries', 'num_queries'),
        ('Network RX Bytes', 'net_rx_bytes'),
        ('Network TX Bytes', 'net_tx_bytes'),
        ('IO Read Bytes', 'io_read_bytes'),
        ('IO Write Bytes', 'io_write_bytes'),
        ('IO Max Scratch Size', 'io_max_scratch_size'),
        ('IO Current Scratch Size', 'io_cur_scratch_size'),
        ('CPU Using (%)', 'cpu_using'),
    ]
    if is_legacy_server():
        del fields[3]
    q = 'query($sess_id:String) {' \
        '  compute_session(sess_id:$sess_id) { $fields }' \
        '}'
    q = q.replace('$fields', ' '.join(item[1] for item in fields))
    v = {'sess_id': sess_id_or_alias}
    with Session() as session:
        try:
            resp = session.Admin.query(q, v)
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if resp['compute_session']['sess_id'] is None:
            print('There is no such running compute session.')
            return
        print('Session detail:\n---------------')
        for i, value in enumerate(resp['compute_session'].values()):
            if fields[i][1] in ['mem_cur_bytes', 'mem_max_bytes']:
                value = round(value / 2 ** 20, 1)
            print(fields[i][0] + ': ' + str(value))
