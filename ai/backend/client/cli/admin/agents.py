# from tabulate import tabulate
#
# from ...admin import Admin
# from ..pretty import print_fail
from . import admin


@admin.register_command
def agents(args):
    '''
    List and manage agents.
    '''
