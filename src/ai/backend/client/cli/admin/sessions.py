import sys
import asyncio

import click
from tabulate import tabulate

from . import admin
from ...session import Session, is_legacy_server
from ..pretty import print_error
from ...compat import current_loop


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
    def execute_paginated_query(session, fields, limit, offset):
        q = 'query($limit:Int!, $offset:Int!, $ak:String, $status:String) {' \
            '  compute_sessions(limit:$limit, offset:$offset, access_key:$ak, status:$status) { $fields }' \
            '}'
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
        return resp['compute_sessions']

    def round_mem(results):
        for item in results:
            if 'mem_cur_bytes' in item:
                item['mem_cur_bytes'] = round(item['mem_cur_bytes'] / 2 ** 20, 1)
            if 'mem_max_bytes' in item:
                item['mem_max_bytes'] = round(item['mem_max_bytes'] / 2 ** 20, 1)
        return results

    def _generate_paginated_results(session, fields, required_count, paginating_limit, id_only):
        offset = 0
        is_first = True
        while offset < required_count:
            limit = min(paginating_limit, required_count - offset)
            results = execute_paginated_query(session, fields, limit, offset)
            offset += paginating_limit
            results = round_mem(results)

            if id_only:
                yield '\n'.join([item['sess_id'] for item in results]) + '\n'
            else:
                table = tabulate([item.values() for item in results], headers=(item[0] for item in fields))
                if is_first:
                    is_first = False
                else:
                    table_rows = table.split('\n')
                    table = '\n'.join(table_rows[2:])
                yield table + '\n'

    fields = [
        ('Session ID', 'sess_id'),
    ]
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
        ])
        if is_legacy_server():
            del fields[2]

    # get count of sessions
    q = 'query($ak:String, $status:String) {' \
        '  count_compute_sessions(access_key:$ak, status:$status) { count }' \
        '}'
    v = {
        'status': status if status != 'ALL' else None,
        'ak': access_key,
    }

    with Session() as session:
        try:
            resp = session.Admin.query(q, v)
        except Exception as e:
            print_error(e)
            sys.exit(1)
        total_count = resp['count_compute_sessions']['count']

        if total_count == 0:
            print('There are no compute sessions currently {0}.'.format(status.lower()))
            return
        
        paginating_limit = 10
        if all:
            click.echo_via_pager(_generate_paginated_results(
                session, fields, total_count, paginating_limit, id_only))
        else:
            results = execute_paginated_query(session, fields, paginating_limit, 0)
            results = round_mem(results)
            if id_only:
                for item in results:
                    print(item['sess_id'])
            else:
                print(tabulate([item.values() for item in results], 
                                headers=(item[0] for item in fields)))
            if total_count > paginating_limit:
                print("\nMore sessions can be displayed by using --all option")

@admin.command()
@click.argument('sess_id_or_alias', metavar='SESSID')
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
