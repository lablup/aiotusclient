import sys

import click
from tabulate import tabulate

from . import admin
from ...session import Session
from ..pretty import print_error


@admin.command()
@click.option('-i', '--id', 'agent_id', required=True,
              help='The agent Id to inspect.')
def agent(agent_id):
    '''
    Show the information about the given agent.
    '''
    fields = [
        ('ID', 'id'),
        ('Status', 'status'),
        ('Region', 'region'),
        ('First Contact', 'first_contact'),
        ('Mem Slots', 'mem_slots'),
        ('Used Mem Slots', 'used_mem_slots'),
        ('CPU Slots', 'cpu_slots'),
        ('Used CPU Slots', 'used_cpu_slots'),
        ('GPU Slots', 'gpu_slots'),
        ('Used GPU Slots', 'used_gpu_slots'),
    ]
    with Session() as session:
        try:
            agent = session.Agent(agent_id)
            info = agent.info(fields=(item[1] for item in fields))
        except Exception as e:
            print_error(e)
            sys.exit(1)
        rows = []
        for name, key in fields:
            rows.append((name, info[key]))
        print(tabulate(rows, headers=('Field', 'Value')))


@admin.command()
@click.option('-s', '--status', type=str, default='ALIVE',
              help='Filter agents by the given status.')
def agents(status):
    '''
    List and manage agents.
    (admin privilege required)
    '''
    fields = [
        ('ID', 'id'),
        ('Status', 'status'),
        ('Region', 'region'),
        ('First Contact', 'first_contact'),
        ('Mem Slots', 'mem_slots'),
        ('Used Mem Slots', 'used_mem_slots'),
        ('CPU Slots', 'cpu_slots'),
        ('Used CPU Slots', 'used_cpu_slots'),
        ('GPU Slots', 'gpu_slots'),
        ('Used GPU Slots', 'used_gpu_slots'),
    ]
    with Session() as session:
        try:
            items = session.Agent.list(status, fields=(item[1] for item in fields))
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if len(items) == 0:
            print('There are no matching agents.')
            return
        print(tabulate((item.values() for item in items),
                       headers=(item[0] for item in fields)))
