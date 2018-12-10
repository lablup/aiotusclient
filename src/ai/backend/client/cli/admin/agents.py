import sys

from tabulate import tabulate

from ...session import Session
from ..pretty import print_error
from . import admin


@admin.register_command
def agent(args):
    '''
    Show the information about the given agent.
    '''
    fields = [
        ('ID', 'id'),
        ('Status', 'status'),
        ('Region', 'region'),
        ('First Contact', 'first_contact'),
        ('Total CPU Cores', 'cpu_slots'),
        ('Allocated CPU Cores', 'used_cpu_slots'),
        ('CPU Usage (%)', 'cpu_cur_pct'),
        ('Total Memory (MiB)', 'mem_slots'),
        ('Allocated Memory (MiB)', 'used_mem_slots'),
        ('Used Memory (MiB)', 'mem_cur_bytes'),
        ('Total GPU Cores', 'gpu_slots'),
        ('Used GPU Cores', 'used_gpu_slots'),
    ]
    with Session() as session:
        try:
            agent = session.Agent(args.id)
            info = agent.info(fields=(item[1] for item in fields))
        except Exception as e:
            print_error(e)
            sys.exit(1)
        rows = []
        for name, key in fields:
            if key == 'mem_cur_bytes':
                info[key] = round(info[key] / 2 ** 20, 1)
            rows.append((name, info[key]))
        print(tabulate(rows, headers=('Field', 'Value')))


agent.add_argument('-i', '--id', type=str, required=True,
                   help='The agent ID to inspect.')


@admin.register_command
def agents(args):
    '''
    List and manage agents.
    (admin privilege required)
    '''
    fields = [
        ('ID', 'id'),
        ('Status', 'status'),
        ('Region', 'region'),
        ('First Contact', 'first_contact'),
        ('Total CPU Cores', 'cpu_slots'),
        ('Allocated CPU Cores', 'used_cpu_slots'),
        ('CPU Usage (%)', 'cpu_cur_pct'),
        ('Total Memory (MiB)', 'mem_slots'),
        ('Allocated Memory (MiB)', 'used_mem_slots'),
        ('Used Memory (MiB)', 'mem_cur_bytes'),
        ('Total GPU Cores', 'gpu_slots'),
        ('Used GPU Cores', 'used_gpu_slots'),
    ]
    with Session() as session:
        try:
            items = session.Agent.list(args.status,
                                       fields=(item[1] for item in fields))
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if len(items) == 0:
            print('There are no matching agents.')
            return
        for item in items:
            item['mem_cur_bytes'] = round(item['mem_cur_bytes'] / 2 ** 20, 1)
        print(tabulate((item.values() for item in items),
                       headers=(item[0] for item in fields)))


agents.add_argument('-s', '--status', type=str, default='ALIVE',
                    help='Filter agents by the given status.')
