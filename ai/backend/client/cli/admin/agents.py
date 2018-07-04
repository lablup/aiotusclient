import sys

from tabulate import tabulate

from ...exceptions import BackendError
from ...session import Session
from ..pretty import print_fail
from . import admin


@admin.register_command
def agents(args):
    '''
    List and manage agents.
    '''
    fields = [
        ('ID', 'id'),
        ('Status', 'status'),
        ('First Contact', 'first_contact'),
        ('Mem.Slots', 'mem_slots'),
        ('CPU Slots', 'cpu_slots'),
        ('GPU Slots', 'gpu_slots'),
    ]
    with Session() as session:
        try:
            items = session.Agent.list(args.status,
                                       fields=(item[1] for item in fields))
        except BackendError as e:
            print_fail(str(e))
            sys.exit(1)
        if len(items) == 0:
            print('There are no matching agents.')
            return
        print(tabulate((item.values() for item in items),
                       headers=(item[0] for item in fields)))


agents.add_argument('-s', '--status', type=str, default='ALIVE',
                    help='Filter agents by the given status.')
